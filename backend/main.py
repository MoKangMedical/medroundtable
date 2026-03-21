from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime
import uvicorn

from backend.models import RoundTable, A2AMessage, RoundTableStatus, ResearchOutput, AgentRole, MessageType
from agents.orchestrator import orchestrator
from backend.database import SessionLocal, SessionHistory, User, init_db

# 导入新的路由
from backend.routers import protocols, databases, analysis

app = FastAPI(
    title="MedRoundTable API",
    description="A2A 医学科研协作平台 API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 数据模型 ============

class CreateRoundTableRequest(BaseModel):
    title: str
    clinical_question: str
    preferred_expert: Optional[str] = None
    human_participants: List[Dict[str, Any]] = Field(default_factory=list)
    secondme_shades: List[Dict[str, Any]] = Field(default_factory=list)
    ai_pack: Optional[Dict[str, Any]] = None
    collaboration_label: Optional[str] = None
    auto_discussion: bool = False
    human_can_interrupt: bool = True

class SendMessageRequest(BaseModel):
    content: str
    to_role: str = "all"

class RoundTableResponse(BaseModel):
    id: str
    title: str
    clinical_question: str
    status: str
    participants: List[str]
    preferred_expert: Optional[str]
    human_participants: List[Dict[str, Any]]
    secondme_shades: List[Dict[str, Any]]
    ai_pack: Optional[Dict[str, Any]]
    collaboration_label: Optional[str]
    auto_discussion: bool
    human_can_interrupt: bool
    current_round: int
    created_at: datetime
    completed_at: Optional[datetime]

class MessageResponse(BaseModel):
    id: str
    from_role: str
    to_role: str
    type: str
    content: str
    created_at: datetime
    metadata: Dict[str, Any]

# ============ 存储 ============
roundtables: Dict[str, RoundTable] = orchestrator.sessions
SYSTEM_USER_EMAIL = "system@medroundtable.local"
SYSTEM_USER_NAME = "MedRoundTable System"
PERSISTENCE_CALLBACK_REGISTERED = False


def _ensure_system_user(db) -> User:
    user = db.query(User).filter(User.email == SYSTEM_USER_EMAIL).first()
    if user:
        return user

    user = User(
        id=str(uuid.uuid4()),
        email=SYSTEM_USER_EMAIL,
        name=SYSTEM_USER_NAME,
        is_active=True,
        is_verified=True,
        is_oauth_user=False,
    )
    user.set_password(uuid.uuid4().hex)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _role_from_value(value: Any):
    if isinstance(value, str) and value in AgentRole._value2member_map_:
        return AgentRole(value)
    return value


def _message_type_from_value(value: Any):
    if isinstance(value, str) and value in MessageType._value2member_map_:
        return MessageType(value)
    return MessageType.FEEDBACK


def _roundtable_status_from_value(value: Optional[str]) -> RoundTableStatus:
    if value and value in RoundTableStatus._value2member_map_:
        return RoundTableStatus(value)
    if value == "completed":
        return RoundTableStatus.COMPLETED
    if value == "active":
        return RoundTableStatus.PROBLEM_PRESENTATION
    return RoundTableStatus.INIT


def _serialize_message(message: A2AMessage) -> Dict[str, Any]:
    from_role = message.from_role.value if hasattr(message.from_role, "value") else str(message.from_role)
    to_role = message.to_role.value if hasattr(message.to_role, "value") else str(message.to_role)
    msg_type = message.type.value if hasattr(message.type, "value") else str(message.type)
    return {
        "id": message.id,
        "session_id": message.session_id,
        "from_role": from_role,
        "to_role": to_role,
        "type": msg_type,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
        "metadata": message.metadata or {},
    }


def _deserialize_message(payload: Dict[str, Any]) -> A2AMessage:
    created_at_raw = payload.get("created_at")
    created_at = datetime.fromisoformat(created_at_raw) if created_at_raw else datetime.utcnow()
    return A2AMessage(
        id=payload.get("id", str(uuid.uuid4())),
        session_id=payload.get("session_id", ""),
        from_role=_role_from_value(payload.get("from_role", "user")),
        to_role=_role_from_value(payload.get("to_role", "all")),
        type=_message_type_from_value(payload.get("type")),
        content=payload.get("content", ""),
        metadata=payload.get("metadata") or {},
        created_at=created_at,
    )


def _extract_current_stage(roundtable: RoundTable) -> Optional[str]:
    if roundtable.messages:
        for message in reversed(roundtable.messages):
            stage = (message.metadata or {}).get("stage")
            if stage:
                return stage
    return roundtable.status.value


def _estimate_progress(roundtable: RoundTable) -> int:
    if roundtable.status == RoundTableStatus.COMPLETED:
        return 100
    return min(20 + roundtable.current_round * 9, 95)


def _dump_model(model: Any) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _persist_roundtable(roundtable: RoundTable):
    with SessionLocal() as db:
        user = _ensure_system_user(db)
        history = db.query(SessionHistory).filter(SessionHistory.session_id == roundtable.id).first()
        messages_payload = [_serialize_message(message) for message in roundtable.messages]
        current_stage = _extract_current_stage(roundtable)
        client_context = {
            "preferred_expert": roundtable.preferred_expert,
            "human_participants": roundtable.human_participants,
            "secondme_shades": roundtable.secondme_shades,
            "ai_pack": roundtable.ai_pack,
            "collaboration_label": roundtable.collaboration_label,
            "auto_discussion": roundtable.auto_discussion,
            "human_can_interrupt": roundtable.human_can_interrupt,
        }

        if not history:
            history = SessionHistory(
                user_id=user.id,
                session_id=roundtable.id,
                title=roundtable.title,
                clinical_question=roundtable.clinical_question,
                status=roundtable.status.value,
                progress=_estimate_progress(roundtable),
                current_stage=current_stage,
                messages=messages_payload,
                created_at=roundtable.created_at,
                updated_at=datetime.utcnow(),
                completed_at=roundtable.completed_at,
            )
            db.add(history)
        else:
            history.title = roundtable.title
            history.clinical_question = roundtable.clinical_question
            history.status = roundtable.status.value
            history.progress = _estimate_progress(roundtable)
            history.current_stage = current_stage
            history.messages = messages_payload
            history.updated_at = datetime.utcnow()
            history.completed_at = roundtable.completed_at

        problem_analysis = history.problem_analysis or {}
        if isinstance(problem_analysis, dict):
            problem_analysis["client_context"] = client_context
            history.problem_analysis = problem_analysis

        if roundtable.output:
            history.study_design = _dump_model(roundtable.output.study_design)
            history.crf_template = _dump_model(roundtable.output.crf_template)
            history.analysis_plan = _dump_model(roundtable.output.analysis_plan)

        db.commit()


def _append_message_to_history(message: A2AMessage):
    with SessionLocal() as db:
        user = _ensure_system_user(db)
        history = db.query(SessionHistory).filter(SessionHistory.session_id == message.session_id).first()
        if not history:
            metadata = message.metadata or {}
            history = SessionHistory(
                user_id=user.id,
                session_id=message.session_id,
                title=metadata.get("title") or f"圆桌 {message.session_id}",
                clinical_question=metadata.get("clinical_question") or "待补充临床问题",
                status="active",
                progress=20,
                current_stage=metadata.get("stage"),
                messages=[],
            )
            db.add(history)

        messages = history.messages or []
        if not any(existing.get("id") == message.id for existing in messages):
            messages.append(_serialize_message(message))
            history.messages = messages

        roundtable = roundtables.get(message.session_id)
        if roundtable:
            history.title = roundtable.title
            history.clinical_question = roundtable.clinical_question
            history.status = roundtable.status.value
            history.progress = _estimate_progress(roundtable)
            history.current_stage = _extract_current_stage(roundtable)
            history.completed_at = roundtable.completed_at
        elif message.metadata.get("stage"):
            history.current_stage = message.metadata["stage"]

        if message.metadata.get("is_final_summary"):
            history.status = RoundTableStatus.COMPLETED.value
            history.progress = 100
            history.completed_at = datetime.utcnow()

        history.updated_at = datetime.utcnow()
        db.commit()


def _hydrate_roundtable(session_id: str) -> Optional[RoundTable]:
    existing = roundtables.get(session_id)
    if existing:
        return existing

    with SessionLocal() as db:
        history = db.query(SessionHistory).filter(SessionHistory.session_id == session_id).first()
        if not history:
            return None

        messages = [_deserialize_message(payload) for payload in (history.messages or [])]
        roundtable = RoundTable(
            id=history.session_id,
            title=history.title,
            clinical_question=history.clinical_question,
            status=_roundtable_status_from_value(history.status),
            participants=list(AgentRole),
            messages=messages,
            preferred_expert=((history.problem_analysis or {}).get("client_context") or {}).get("preferred_expert"),
            human_participants=((history.problem_analysis or {}).get("client_context") or {}).get("human_participants") or [],
            secondme_shades=((history.problem_analysis or {}).get("client_context") or {}).get("secondme_shades") or [],
            ai_pack=((history.problem_analysis or {}).get("client_context") or {}).get("ai_pack"),
            collaboration_label=((history.problem_analysis or {}).get("client_context") or {}).get("collaboration_label"),
            auto_discussion=bool(((history.problem_analysis or {}).get("client_context") or {}).get("auto_discussion")),
            human_can_interrupt=((history.problem_analysis or {}).get("client_context") or {}).get("human_can_interrupt", True),
            current_round=max(
                [int((message.metadata or {}).get("round", 0)) for message in messages] or [0]
            ),
            created_at=history.created_at or datetime.utcnow(),
            completed_at=history.completed_at,
        )
        roundtables[session_id] = roundtable
        return roundtable


def _build_roundtable_response(roundtable: RoundTable) -> RoundTableResponse:
    return RoundTableResponse(
        id=roundtable.id,
        title=roundtable.title,
        clinical_question=roundtable.clinical_question,
        status=roundtable.status.value,
        participants=[participant.value for participant in roundtable.participants],
        preferred_expert=roundtable.preferred_expert,
        human_participants=roundtable.human_participants,
        secondme_shades=roundtable.secondme_shades,
        ai_pack=roundtable.ai_pack,
        collaboration_label=roundtable.collaboration_label,
        auto_discussion=roundtable.auto_discussion,
        human_can_interrupt=roundtable.human_can_interrupt,
        current_round=roundtable.current_round,
        created_at=roundtable.created_at,
        completed_at=roundtable.completed_at
    )


async def _persist_message_callback(message: A2AMessage):
    _append_message_to_history(message)

# ============ API端点 ============

@app.get("/")
async def root():
    return {
        "name": "MedRoundTable API",
        "version": "2.0.0",
        "description": "A2A + STELLA 医学科研协作平台 - 整合 997 项技能，其中 869 项来自 OpenClaw 包装层",
        "features": [
            "V1.0 圆桌协作",
            "V2.0 技能市场",
            "STELLA Manager-Dev-Critic",
            "OpenClaw Medical Skills 包装层",
            "V2.0 数据库浏览器",
            "V2.0 临床试验设计",
        ],
        "docs": {
            "v1": "/api/v1/",
            "v2": "/api/v2/",
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# ---- Agent 信息 ----

@app.get("/api/v1/agents")
async def get_agents():
    """获取所有Agent信息"""
    return orchestrator.get_agent_info()

# ---- 圆桌会管理 ----

@app.post("/api/v1/roundtables", response_model=RoundTableResponse)
async def create_roundtable(request: CreateRoundTableRequest):
    """创建新的圆桌会"""
    roundtable = await orchestrator.create_roundtable(
        title=request.title,
        clinical_question=request.clinical_question,
        preferred_expert=request.preferred_expert,
        human_participants=request.human_participants,
        secondme_shades=request.secondme_shades,
        ai_pack=request.ai_pack,
        collaboration_label=request.collaboration_label,
        auto_discussion=request.auto_discussion,
        human_can_interrupt=request.human_can_interrupt
    )
    roundtables[roundtable.id] = roundtable
    _persist_roundtable(roundtable)

    return _build_roundtable_response(roundtable)

@app.get("/api/v1/roundtables", response_model=List[RoundTableResponse])
async def list_roundtables():
    """列出所有圆桌会"""
    with SessionLocal() as db:
        histories = (
            db.query(SessionHistory)
            .filter(SessionHistory.is_deleted == False)
            .order_by(SessionHistory.updated_at.desc())
            .all()
        )

    responses: List[RoundTableResponse] = []
    for history in histories:
        roundtable = _hydrate_roundtable(history.session_id)
        if roundtable:
            responses.append(_build_roundtable_response(roundtable))
    return responses

@app.get("/api/v1/roundtables/{session_id}", response_model=RoundTableResponse)
async def get_roundtable(session_id: str):
    """获取圆桌会详情"""
    rt = _hydrate_roundtable(session_id)
    if not rt:
        raise HTTPException(status_code=404, detail="RoundTable not found")

    return _build_roundtable_response(rt)

@app.post("/api/v1/roundtables/{session_id}/start")
async def start_roundtable(session_id: str):
    """开始圆桌讨论"""
    rt = _hydrate_roundtable(session_id)
    if not rt:
        raise HTTPException(status_code=404, detail="RoundTable not found")
    
    if rt.status != RoundTableStatus.INIT:
        raise HTTPException(status_code=400, detail="RoundTable already started")
    
    # 直接挂到当前事件循环，避免 BackgroundTasks 层导致首轮讨论没有真正启动
    asyncio.create_task(orchestrator.start_discussion(session_id))
    _persist_roundtable(rt)
    
    return {"status": "started", "session_id": session_id}

@app.post("/api/v1/roundtables/{session_id}/pause")
async def pause_roundtable(session_id: str):
    """暂停圆桌讨论"""
    rt = _hydrate_roundtable(session_id)
    if not rt:
        raise HTTPException(status_code=404, detail="RoundTable not found")
    
    rt.status = RoundTableStatus.INIT  # 简化处理
    _persist_roundtable(rt)
    return {"status": "paused", "session_id": session_id}

# ---- 消息管理 ----

@app.get("/api/v1/roundtables/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(session_id: str):
    """获取圆桌会消息列表"""
    rt = _hydrate_roundtable(session_id)
    if not rt:
        raise HTTPException(status_code=404, detail="RoundTable not found")
    
    return [
        MessageResponse(
            id=msg.id,
            from_role=msg.from_role.value if hasattr(msg.from_role, 'value') else str(msg.from_role),
            to_role=msg.to_role.value if hasattr(msg.to_role, 'value') else str(msg.to_role),
            type=msg.type.value,
            content=msg.content,
            created_at=msg.created_at,
            metadata=msg.metadata
        )
        for msg in rt.messages
    ]

@app.post("/api/v1/roundtables/{session_id}/messages")
async def send_message(session_id: str, request: SendMessageRequest):
    """用户发送消息"""
    rt = _hydrate_roundtable(session_id)
    if not rt:
        raise HTTPException(status_code=404, detail="RoundTable not found")
    
    await orchestrator.user_send_message(
        session_id=session_id,
        content=request.content,
        to_role=request.to_role
    )
    _persist_roundtable(rt)
    
    return {"status": "sent"}

@app.get("/api/v1/roundtables/{session_id}/stream")
async def stream_messages(session_id: str):
    """SSE 消息流 - 实时接收Agent消息"""
    rt = _hydrate_roundtable(session_id)
    if not rt:
        raise HTTPException(status_code=404, detail="RoundTable not found")
    
    async def event_generator():
        message_queue = asyncio.Queue()
        
        async def on_new_message(message: A2AMessage):
            await message_queue.put(message)
        
        # 注册回调
        orchestrator.register_message_callback(on_new_message)
        
        try:
            while True:
                try:
                    message = await asyncio.wait_for(message_queue.get(), timeout=30.0)
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'type': 'ping'})}\n\n"
                    continue

                if message.session_id != session_id:
                    continue

                data = {
                    "id": message.id,
                    "from_role": message.from_role.value if hasattr(message.from_role, 'value') else str(message.from_role),
                    "to_role": message.to_role.value if hasattr(message.to_role, 'value') else str(message.to_role),
                    "type": message.type.value,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                    "metadata": message.metadata
                }
                yield f"data: {json.dumps(data)}\n\n"
        finally:
            orchestrator.unregister_message_callback(on_new_message)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# ---- 成果输出 ----

@app.get("/api/v1/roundtables/{session_id}/output")
async def get_output(session_id: str):
    """获取研究成果"""
    rt = _hydrate_roundtable(session_id)
    if not rt:
        raise HTTPException(status_code=404, detail="RoundTable not found")
    
    # 生成研究输出（简化版）
    output = {
        "study_protocol": generate_study_protocol(rt),
        "crf_template": generate_crf_template(rt),
        "analysis_plan": generate_analysis_plan(rt),
        "operation_manual": generate_operation_manual(rt),
        "generated_at": datetime.utcnow().isoformat()
    }
    
    return output

def generate_study_protocol(rt: RoundTable) -> str:
    """生成研究方案"""
    return f"""# 临床研究方案

## 研究标题
{rt.title}

## 研究背景
{rt.clinical_question}

## 研究设计
多中心、前瞻性队列研究

## 讨论记录摘要
本次圆桌会共有 {len(rt.messages)} 条讨论记录，涵盖：
- 临床问题分析
- 文献调研
- 研究方案设计
- 统计分析计划
- 数据采集设计
- 执行计划制定

（完整内容基于讨论记录自动生成）
"""

def generate_crf_template(rt: RoundTable) -> dict:
    """生成CRF模板"""
    return {
        "sections": [
            {"name": "人口学信息", "fields": ["年龄", "性别", "BMI", "民族"]},
            {"name": "病史资料", "fields": ["糖尿病病程", "并发症", "合并用药"]},
            {"name": "实验室检查", "fields": ["HbA1c", "空腹血糖", "血脂", "肾功能"]},
            {"name": "终点事件", "fields": ["心血管事件", "全因死亡", "不良反应"]}
        ]
    }

def generate_analysis_plan(rt: RoundTable) -> dict:
    """生成分析计划"""
    return {
        "primary_analysis": "Cox比例风险模型",
        "secondary_analyses": ["Kaplan-Meier生存分析", "多因素回归", "亚组分析"],
        "sample_size": 800,
        "significance_level": "α=0.05",
        "software": "R 4.3.0 或 SAS 9.4"
    }

def generate_operation_manual(rt: RoundTable) -> str:
    """生成操作手册"""
    return """# 研究操作手册

## 1. 人员职责
- 研究医生：患者筛选、知情同意
- 研究护士：数据采集、随访
- 数据管理员：质量控制

## 2. 操作流程
1. 筛选期（-7天）：签署知情同意
2. 基线期（Day 0）：入组评估
3. 随访期：1、3、6、12个月

## 3. 质量控制
- 双人录入
- 源数据核查
- 定期监查

## 4. 应急预案
详见完整SOP文档
"""

# 启动时初始化
@app.on_event("startup")
async def startup_event():
    # 初始化数据库
    init_db()
    global PERSISTENCE_CALLBACK_REGISTERED
    if not PERSISTENCE_CALLBACK_REGISTERED:
        orchestrator.register_message_callback(_persist_message_callback)
        PERSISTENCE_CALLBACK_REGISTERED = True
    
    print("🚀 MedRoundTable API 启动成功")
    print("📚 文档地址: http://localhost:8000/docs")

# ============ V2.0 新增：技能市场与数据库API ============

# 技能市场API
from backend.routes.skills.marketplace import router as skills_router
app.include_router(skills_router)

# 生物医学数据库API
from backend.routes.databases.biomedical import router as databases_router
app.include_router(databases_router)

# 临床试验设计API
from backend.routes.trials.designer import router as trials_router
app.include_router(trials_router)

# STELLA 架构编排 API
from backend.routes.stella import router as stella_router
app.include_router(stella_router)

# ============ 自研认证系统 (替代Second Me OAuth) ============
from backend.routes.auth.custom_auth import router as auth_router
app.include_router(auth_router)

# 注册原有路由
from backend.routes.export import router as export_router
from backend.routes.literature import router as literature_router
from backend.routes.templates import router as templates_router
from backend.routes.user import router as user_router

app.include_router(export_router)
app.include_router(literature_router)
app.include_router(templates_router)
app.include_router(user_router)

# ============ A2A 集成 (可选，不依赖Second Me) ============
# 注意：A2A功能现在不强制依赖Second Me OAuth
from backend.a2a_integration import router as a2a_router
app.include_router(a2a_router)

# ============ V2.0 API 概览端点 ============
@app.get("/api/v2/")
async def api_v2_root():
    """V2.0 API 概览"""
    from backend.services.platform_catalog import get_platform_stats
    return {
        "version": "2.0.0",
        "name": "MedRoundTable API V2",
        "description": "整合 997 项技能的医学科研协作平台，内含 STELLA Manager-Dev-Critic 编排层",
        "features": [
            "14位专业医学专家协作",
            "STELLA Manager-Dev-Critic",
            "997项技能市场",
            "869项 OpenClaw Medical Skills 包装层",
            f"{get_platform_stats()['database_total']}个已编目生物医学数据库",
            "智能临床试验设计",
            "生物信息学分析",
            "AI研究辅助"
        ],
        "endpoints": {
            "skills": "/api/v2/skills/",
            "stella": "/api/v2/stella/architecture",
            "databases": "/api/v2/databases/",
            "capabilities": "/api/v2/capabilities",
            "trials": "/api/v2/trials/",
            "agents": "/api/v1/agents",
            "roundtables": "/api/v1/roundtables"
        }
    }

@app.get("/api/v2/stats")
async def api_v2_stats():
    """V2.0 平台统计"""
    from skills.registry import skill_registry
    from backend.services.platform_catalog import (
        get_platform_capability_lanes,
        get_platform_source_packages,
        get_platform_stats,
    )

    platform_stats = get_platform_stats()
    
    return {
        "skills": skill_registry.get_stats(),
        "databases": {
            "total": platform_stats["database_total"],
            "categories": platform_stats["database_categories"],
            "category_count": platform_stats["database_categories_total"],
        },
        "agents": {
            "total": platform_stats["experts_total"],
            "categories": ["核心临床团队", "生信套件", "研究支持团队"]
        },
        "stella": {
            "meta_roles": platform_stats["stella_meta_roles"],
            "architecture": "Manager-Dev-Critic",
            "status": "integrated"
        },
        "algorithms": {
            "total_lanes": platform_stats["capability_total"],
            "capability_lanes": get_platform_capability_lanes(),
            "source_packages": get_platform_source_packages(),
        },
        "version": "2.0.0",
        "status": "operational"
    }


@app.get("/api/v2/capabilities")
async def api_v2_capabilities():
    """平台数据库与算法能力总览"""
    from backend.services.platform_catalog import (
        get_platform_capability_lanes,
        get_platform_databases,
        get_platform_source_packages,
        get_platform_stats,
    )

    stats = get_platform_stats()
    return {
        "stats": stats,
        "capability_lanes": get_platform_capability_lanes(),
        "source_packages": get_platform_source_packages(),
        "databases": get_platform_databases(),
    }

# ============ 注册新路由 ============
app.include_router(protocols.router)
app.include_router(databases.router)
app.include_router(analysis.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
