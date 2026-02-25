"""
Second Me A2A Integration Module
提供与 Second Me 平台的 A2A (Agent-to-Agent) 协议集成
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import json

router = APIRouter(prefix="/api/a2a", tags=["A2A Integration"])

# ============ 数据模型 ============

class MessageType(str, Enum):
    PROPOSAL = "proposal"
    QUESTION = "question"
    FEEDBACK = "feedback"
    AGREEMENT = "agreement"
    OBJECTION = "objection"
    SUMMARY = "summary"
    TASK = "task"
    RESPONSE = "response"
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"

class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class AgentIdentity(BaseModel):
    agent_id: str
    agent_name: str
    system: str = "MedRoundTable"
    version: str = "1.0.0"
    capabilities: List[str] = []

class A2AMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender: AgentIdentity
    recipient: AgentIdentity
    message_type: MessageType
    content: str
    metadata: Dict[str, Any] = {}
    context: Dict[str, Any] = {}

class DiscoveryRequest(BaseModel):
    agent_id: str
    agent_name: str
    capabilities: List[str]
    endpoint: str

class DiscoveryResponse(BaseModel):
    agents: List[AgentIdentity]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TaskRequest(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str
    description: str
    assignee: Optional[AgentIdentity] = None
    priority: Priority = Priority.NORMAL
    deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None

# ============ 存储 ============

# 存储已发现的 Second Me agents
discovered_agents: Dict[str, AgentIdentity] = {}

# 存储 A2A 消息历史
message_history: List[A2AMessage] = []

# 存储任务
active_tasks: Dict[str, TaskRequest] = {}

# ============ API 端点 ============

@router.get("/discovery")
async def discovery():
    """
    A2A Agent 发现端点
    Second Me 平台和其他 Agent 可以通过此端点发现 MedRoundTable
    """
    return {
        "agent_system": "MedRoundTable",
        "version": "1.0.0",
        "agents": [
            {
                "id": "clinical_director",
                "name": "资深临床主任",
                "role": "临床问题识别与研究价值评估",
                "capabilities": ["clinical_assessment", "research_design", "feasibility_analysis"]
            },
            {
                "id": "phd_student",
                "name": "临床博士生", 
                "role": "文献检索与研究协调",
                "capabilities": ["literature_review", "coordination", "documentation"]
            },
            {
                "id": "epidemiologist",
                "name": "临床流行病学专家",
                "role": "研究设计与方案制定", 
                "capabilities": ["study_design", "protocol_development", "quality_control"]
            },
            {
                "id": "statistician",
                "name": "数据统计专家",
                "role": "统计分析与数据管理",
                "capabilities": ["statistical_analysis", "data_management", "visualization"]
            },
            {
                "id": "research_nurse",
                "name": "研究护士",
                "role": "数据采集与质量控制", 
                "capabilities": ["data_collection", "quality_assurance", "operations"]
            }
        ],
        "endpoints": {
            "message": "/api/a2a/message",
            "task": "/api/a2a/task",
            "status": "/api/a2a/status"
        },
        "capabilities": [
            "agent_discovery",
            "agent_communication",
            "task_orchestration",
            "research_collaboration"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/register")
async def register_agent(agent: DiscoveryRequest):
    """
    注册外部 Agent（如 Second Me AI）
    """
    agent_identity = AgentIdentity(
        agent_id=agent.agent_id,
        agent_name=agent.agent_name,
        capabilities=agent.capabilities
    )
    discovered_agents[agent.agent_id] = agent_identity
    
    return {
        "status": "registered",
        "agent_id": agent.agent_id,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/message")
async def send_message(message: A2AMessage):
    """
    接收来自 Second Me 或其他 Agent 的 A2A 消息
    """
    # 存储消息
    message_history.append(message)
    
    # 根据消息类型处理
    response_content = await process_a2a_message(message)
    
    # 生成响应
    response = A2AMessage(
        sender=AgentIdentity(
            agent_id="medroundtable_system",
            agent_name="MedRoundTable",
            capabilities=["research_orchestration"]
        ),
        recipient=message.sender,
        message_type=MessageType.RESPONSE,
        content=response_content,
        context={
            "conversation_id": message.context.get("conversation_id"),
            "parent_message_id": message.id
        }
    )
    
    return {
        "status": "received",
        "message_id": message.id,
        "response": response.dict(),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/messages")
async def get_messages(
    agent_id: Optional[str] = None,
    message_type: Optional[MessageType] = None,
    limit: int = 50
):
    """
    获取 A2A 消息历史
    """
    messages = message_history
    
    if agent_id:
        messages = [m for m in messages if m.sender.agent_id == agent_id or m.recipient.agent_id == agent_id]
    
    if message_type:
        messages = [m for m in messages if m.message_type == message_type]
    
    messages = messages[-limit:]
    
    return {
        "messages": [m.dict() for m in messages],
        "total": len(message_history),
        "returned": len(messages)
    }

@router.post("/task")
async def create_task(task: TaskRequest, background_tasks: BackgroundTasks):
    """
    创建 A2A 任务
    Second Me 或其他 Agent 可以委托任务给 MedRoundTable
    """
    active_tasks[task.task_id] = task
    
    # 异步执行任务
    background_tasks.add_task(execute_a2a_task, task)
    
    return {
        "task_id": task.task_id,
        "status": "accepted",
        "estimated_completion": "pending",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    查询任务状态
    """
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    return {
        "task_id": task_id,
        "task_type": task.task_type,
        "status": "in_progress",  # 实际应从任务执行状态获取
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/status")
async def system_status():
    """
    获取系统状态
    """
    return {
        "status": "healthy",
        "agents_available": 5,
        "active_tasks": len(active_tasks),
        "discovered_agents": len(discovered_agents),
        "messages_exchanged": len(message_history),
        "a2a_version": "1.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/webhook/secondme")
async def secondme_webhook(request: Request):
    """
    Second Me 平台 webhook 端点
    接收 Second Me 的事件通知
    """
    payload = await request.json()
    
    # 处理 Second Me 事件
    event_type = payload.get("event_type")
    
    if event_type == "agent.online":
        # Second Me Agent 上线
        agent_data = payload.get("agent")
        discovered_agents[agent_data["id"]] = AgentIdentity(**agent_data)
        
    elif event_type == "agent.offline":
        # Second Me Agent 下线
        agent_id = payload.get("agent_id")
        if agent_id in discovered_agents:
            del discovered_agents[agent_id]
            
    elif event_type == "message.received":
        # 收到来自 Second Me 的消息
        message_data = payload.get("message")
        message_history.append(A2AMessage(**message_data))
    
    return {"status": "ok"}

# ============ 辅助函数 ============

async def process_a2a_message(message: A2AMessage) -> str:
    """
    处理 A2A 消息并生成响应
    """
    if message.message_type == MessageType.QUESTION:
        return f"MedRoundTable 收到您的问题。我们的 {'、'.join([a.name for a in discovered_agents.values()])} 将协助您。"
    
    elif message.message_type == MessageType.PROPOSAL:
        return "MedRoundTable 收到您的研究提议。临床主任 Agent 将评估其价值和可行性。"
    
    elif message.message_type == MessageType.TASK:
        return "任务已接收，正在分配给合适的 Agent 执行。"
    
    elif message.message_type == MessageType.HEARTBEAT:
        return "heartbeat_ack"
    
    else:
        return f"MedRoundTable 已收到您的 {message.message_type} 消息。"

async def execute_a2a_task(task: TaskRequest):
    """
    执行 A2A 任务
    """
    # 这里实现具体的任务执行逻辑
    # 可以调用现有的 orchestrator 功能
    
    if task.task_type == "research_design":
        # 调用研究设计生成
        pass
    elif task.task_type == "literature_review":
        # 调用文献检索
        pass
    elif task.task_type == "data_analysis":
        # 调用统计分析
        pass
    
    # 任务完成后更新状态
    # active_tasks[task.task_id].status = "completed"
