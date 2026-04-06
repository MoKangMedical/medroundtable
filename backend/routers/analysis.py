"""
数据分析API路由
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List

from backend.upload_models import (
    AnalysisCreate,
    AnalysisPlanRequest,
    AnalysisPlanResponse,
    AnalysisResult,
    AnalysisTask,
    DatabaseProfile,
    ExternalAPICall,
    ExternalAPIResponse,
)
from backend.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/analysis", tags=["数据分析"])


@router.get("/types")
async def list_supported_analysis_types():
    """列出当前后台支持的分析类型和适用场景。"""
    return {
        "analysis_types": [
            {
                "type": "descriptive",
                "title": "描述性统计",
                "use_case": "上传数据后的首轮质量检查、变量画像、缺失概览",
            },
            {
                "type": "comparative",
                "title": "组间比较",
                "use_case": "按暴露/队列/治疗组比较连续变量或比例差异",
            },
            {
                "type": "correlation",
                "title": "相关性分析",
                "use_case": "先看变量之间的相关结构、共线性和潜在线索",
            },
            {
                "type": "regression",
                "title": "回归建模",
                "use_case": "建立多因素模型，输出回归系数和显著性结果",
            },
            {
                "type": "custom",
                "title": "自定义分析",
                "use_case": "走 STELLA 规划后进入人工审核或特殊工作流",
            },
        ],
        "count": 5,
    }


@router.get("/databases/{database_id}/profile", response_model=DatabaseProfile)
async def profile_database(
    database_id: str,
    sample_rows: int = 1000,
    max_categories: int = 10,
):
    """为上传数据库生成结构化画像，给前台分析规划直接使用。"""
    try:
        return await AnalysisService.profile_database(
            database_id=database_id,
            sample_rows=sample_rows,
            max_categories=max_categories,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成数据库画像失败: {str(e)}")


@router.post("/plan", response_model=AnalysisPlanResponse)
async def build_analysis_plan(request: AnalysisPlanRequest):
    """结合数据库画像、STELLA 与 skills 自动生成分析规划。"""
    try:
        return await AnalysisService.build_analysis_plan(
            database_id=request.database_id,
            objective=request.objective,
            clinical_question=request.clinical_question,
            research_stage=request.research_stage,
            preferred_analysis_types=request.preferred_analysis_types,
            required_outputs=request.required_outputs,
            constraints=request.constraints,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成分析规划失败: {str(e)}")


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
    return AnalysisResult(
        task_id=task_id,
        status="completed",
        summary=task.result.get("summary") if task.result else None,
        statistics=task.result.get("statistics") if task.result else None,
        charts=task.result.get("charts") if task.result else None,
        tables=task.result.get("tables") if task.result else None,
        recommendations=task.result.get("recommendations") if task.result else None,
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
    # TODO: 实现删除逻辑
    return {"message": "任务删除功能开发中", "task_id": task_id}
