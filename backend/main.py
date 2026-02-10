from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
from datetime import datetime
import uvicorn

from backend.models import RoundTable, A2AMessage, RoundTableStatus, ResearchOutput
from agents.orchestrator import orchestrator

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

class SendMessageRequest(BaseModel):
    content: str
    to_role: str = "all"

class RoundTableResponse(BaseModel):
    id: str
    title: str
    clinical_question: str
    status: str
    participants: List[str]
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
# 实际项目中使用数据库
roundtables: Dict[str, RoundTable] = {}

# ============ API端点 ============

@app.get("/")
async def root():
    return {
        "name": "MedRoundTable API",
        "version": "1.0.0",
        "description": "A2A 医学科研协作平台"
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
        clinical_question=request.clinical_question
    )
    roundtables[roundtable.id] = roundtable
    
    return RoundTableResponse(
        id=roundtable.id,
        title=roundtable.title,
        clinical_question=roundtable.clinical_question,
        status=roundtable.status.value,
        participants=[p.value for p in roundtable.participants],
        current_round=roundtable.current_round,
        created_at=roundtable.created_at,
        completed_at=roundtable.completed_at
    )

@app.get("/api/v1/roundtables", response_model=List[RoundTableResponse])
async def list_roundtables():
    """列出所有圆桌会"""
    return [
        RoundTableResponse(
            id=rt.id,
            title=rt.title,
            clinical_question=rt.clinical_question,
            status=rt.status.value,
            participants=[p.value for p in rt.participants],
            current_round=rt.current_round,
            created_at=rt.created_at,
            completed_at=rt.completed_at
        )
        for rt in roundtables.values()
    ]

@app.get("/api/v1/roundtables/{session_id}", response_model=RoundTableResponse)
async def get_roundtable(session_id: str):
    """获取圆桌会详情"""
    rt = roundtables.get(session_id)
    if not rt:
        raise HTTPException(status_code=404, detail="RoundTable not found")
    
    return RoundTableResponse(
        id=rt.id,
        title=rt.title,
        clinical_question=rt.clinical_question,
        status=rt.status.value,
        participants=[p.value for p in rt.participants],
        current_round=rt.current_round,
        created_at=rt.created_at,
        completed_at=rt.completed_at
    )

@app.post("/api/v1/roundtables/{session_id}/start")
async def start_roundtable(session_id: str, background_tasks: BackgroundTasks):
    """开始圆桌讨论"""
    rt = roundtables.get(session_id)
    if not rt:
        raise HTTPException(status_code=404, detail="RoundTable not found")
    
    if rt.status != RoundTableStatus.INIT:
        raise HTTPException(status_code=400, detail="RoundTable already started")
    
    # 在后台启动讨论
    background_tasks.add_task(orchestrator.start_discussion, session_id)
    
    return {"status": "started", "session_id": session_id}

@app.post("/api/v1/roundtables/{session_id}/pause")
async def pause_roundtable(session_id: str):
    """暂停圆桌讨论"""
    rt = roundtables.get(session_id)
    if not rt:
        raise HTTPException(status_code=404, detail="RoundTable not found")
    
    rt.status = RoundTableStatus.INIT  # 简化处理
    return {"status": "paused", "session_id": session_id}

# ---- 消息管理 ----

@app.get("/api/v1/roundtables/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(session_id: str):
    """获取圆桌会消息列表"""
    rt = roundtables.get(session_id)
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
    rt = roundtables.get(session_id)
    if not rt:
        raise HTTPException(status_code=404, detail="RoundTable not found")
    
    await orchestrator.user_send_message(
        session_id=session_id,
        content=request.content,
        to_role=request.to_role
    )
    
    return {"status": "sent"}

@app.get("/api/v1/roundtables/{session_id}/stream")
async def stream_messages(session_id: str):
    """SSE 消息流 - 实时接收Agent消息"""
    rt = roundtables.get(session_id)
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
                message = await asyncio.wait_for(message_queue.get(), timeout=30.0)
                if message.session_id == session_id:
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
        except asyncio.TimeoutError:
            yield f"data: {json.dumps({'type': 'ping'})}\n\n"
    
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
    rt = roundtables.get(session_id)
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

# 启动时同步已有的圆桌会
@app.on_event("startup")
async def startup_event():
    print("🚀 MedRoundTable API 启动成功")
    print("📚 文档地址: http://localhost:8000/docs")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
