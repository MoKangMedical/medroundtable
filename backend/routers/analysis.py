"""
数据分析API路由
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List

from backend.upload_models import (
    AnalysisCreate, AnalysisTask, AnalysisResult,
    ExternalAPICall, ExternalAPIResponse
)
from backend.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/analysis", tags=["数据分析"])


@router.post("/tasks", response_model=AnalysisTask)
async def create_analysis_task(create_data: AnalysisCreate):
    """
    创建数据分析任务
    
    支持的分析类型:
    - descriptive: 描述性统计
    - comparative: 比较分析
    - correlation: 相关性分析
    - regression: 回归分析
    - custom: 自定义分析
    """
    try:
        task = await AnalysisService.create_analysis_task(
            name=create_data.name,
            description=create_data.description,
            database_id=create_data.database_id,
            analysis_type=create_data.analysis_type,
            config=create_data.config,
            created_by=None  # TODO: 从认证信息获取
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.get("/tasks/{task_id}", response_model=AnalysisTask)
async def get_analysis_task(task_id: str):
    """获取分析任务详情和状态"""
    task = AnalysisService.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="分析任务不存在")
    return task


@router.get("/tasks/{task_id}/result")
async def get_analysis_result(task_id: str):
    """
    获取分析任务结果
    
    仅当任务状态为 completed 时返回完整结果
    """
    task = AnalysisService.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="分析任务不存在")
    
    if task.status == "pending":
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "任务正在排队中"
        }
    
    if task.status == "running":
        return {
            "task_id": task_id,
            "status": "running",
            "message": "任务正在执行中"
        }
    
    if task.status == "failed":
        return {
            "task_id": task_id,
            "status": "failed",
            "error": task.error_message
        }
    
    # completed
    payload = task.result or {}
    return AnalysisResult(
        task_id=task_id,
        status="completed",
        summary=payload.get("summary") or {
            "message": "任务已完成，但结果仍采用原始结构返回。",
            "analysis_type": task.analysis_type,
        },
        statistics=payload.get("statistics") or payload,
        charts=payload.get("charts"),
        tables=payload.get("tables"),
        recommendations=payload.get("recommendations") or ["请回到数据管理页继续查看原始任务结果。"],
        completed_at=task.completed_at
    )


@router.get("/tasks", response_model=List[AnalysisTask])
async def list_analysis_tasks(
    database_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    获取分析任务列表
    
    支持按数据库ID和状态过滤
    """
    tasks = AnalysisService.get_tasks(
        database_id=database_id,
        status=status,
        skip=skip,
        limit=limit
    )
    return tasks


@router.post("/external", response_model=ExternalAPIResponse)
async def call_external_api(api_call: ExternalAPICall):
    """
    调用外部API进行分析
    
    支持的API提供商:
    - nhanes_analyzer: NHANES数据分析
    - seer_analyzer: SEER肿瘤数据分析
    - medivisual: 医学数据可视化
    - clawbio: ClawBio生物信息学分析
    """
    try:
        response = await AnalysisService.call_external_api(
            database_id=api_call.database_id,
            api_provider=api_call.api_provider,
            endpoint=api_call.endpoint,
            parameters=api_call.parameters,
            callback_url=api_call.callback_url
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API调用失败: {str(e)}")


@router.get("/external/providers")
async def list_external_api_providers():
    """列出支持的外部API提供商"""
    from backend.services.analysis_service import EXTERNAL_APIS
    
    providers = []
    for name, config in EXTERNAL_APIS.items():
        providers.append({
            "name": name,
            "base_url": config["base_url"],
            "endpoints": list(config["endpoints"].keys())
        })
    
    return {
        "providers": providers,
        "count": len(providers)
    }


@router.delete("/tasks/{task_id}")
async def delete_analysis_task(task_id: str):
    """删除分析任务"""
    success = AnalysisService.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="分析任务不存在")
    return {"message": "任务删除成功", "task_id": task_id}
