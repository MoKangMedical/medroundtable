"""
STELLA 架构 API
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.stella import stella_service

router = APIRouter(prefix="/api/v2/stella", tags=["STELLA"])


class StellaWorkflowRequest(BaseModel):
    objective: str = Field(..., description="本次研究目标")
    clinical_question: str = Field(..., description="需要解决的临床问题")
    research_stage: Optional[str] = Field(default=None, description="研究阶段")
    required_outputs: List[str] = Field(default_factory=list, description="期望产出")
    constraints: List[str] = Field(default_factory=list, description="约束条件")


class StellaWorkflowResponse(BaseModel):
    stella_mode: str
    manager: Dict[str, Any]
    dev: Dict[str, Any]
    critic: Dict[str, Any]
    recommended_skills: List[Dict[str, Any]]
    quality_gates: List[str]
    delivery_targets: List[str]


@router.get("/architecture")
async def get_architecture():
    """获取 STELLA 架构说明"""
    return stella_service.get_architecture()


@router.post("/orchestrate", response_model=StellaWorkflowResponse)
async def orchestrate_workflow(request: StellaWorkflowRequest):
    """生成一份 Manager-Dev-Critic 研究执行蓝图"""
    result = stella_service.build_workflow(
        objective=request.objective,
        clinical_question=request.clinical_question,
        research_stage=request.research_stage,
        required_outputs=request.required_outputs,
        constraints=request.constraints,
    )
    return StellaWorkflowResponse(**result)
