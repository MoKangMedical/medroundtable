"""
技能市场API路由
提供技能浏览、搜索、调用功能
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from skills.registry import skill_registry, SkillCategory, SkillSource

router = APIRouter(prefix="/api/v2/skills", tags=["技能市场"])

# ============ 数据模型 ============

class SkillResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    source: str
    version: str
    enabled: bool

class SkillCategoryResponse(BaseModel):
    name: str
    count: int
    skills: List[str]

class SkillStatsResponse(BaseModel):
    total_skills: int
    by_category: Dict[str, int]
    by_source: Dict[str, int]
    enabled: int

class SkillInvokeRequest(BaseModel):
    skill_id: str
    parameters: Optional[Dict[str, Any]] = {}

class SkillInvokeResponse(BaseModel):
    success: bool
    skill_id: str
    result: Any
    message: str

# ============ API端点 ============

@router.get("/", response_model=List[SkillResponse])
async def get_all_skills(
    category: Optional[str] = Query(None, description="按分类筛选"),
    source: Optional[str] = Query(None, description="按来源筛选"),
    enabled_only: bool = Query(True, description="仅显示启用的技能")
):
    """
    获取所有技能列表
    
    参数:
    - category: 分类筛选 (临床/研究/生物信息学/法规合规/AI_ML/数据库/文献/临床试验/药物研发/通用)
    - source: 来源筛选
    - enabled_only: 仅显示启用的技能
    """
    skills = skill_registry.get_all_skills()
    
    # 筛选
    if category:
        try:
            cat = SkillCategory(category)
            skills = [s for s in skills if s.category == cat]
        except ValueError:
            pass
    
    if source:
        try:
            src = SkillSource(source)
            skills = [s for s in skills if s.source == src]
        except ValueError:
            pass
    
    if enabled_only:
        skills = [s for s in skills if s.enabled]
    
    return [
        SkillResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            category=s.category.value,
            source=s.source.value,
            version=s.version,
            enabled=s.enabled
        )
        for s in skills
    ]

@router.get("/search")
async def search_skills(
    q: str = Query(..., description="搜索关键词", min_length=1),
    limit: int = Query(20, description="返回数量限制")
):
    """
    搜索技能
    
    参数:
    - q: 搜索关键词
    - limit: 最大返回数量
    """
    results = skill_registry.search_skills(q)[:limit]
    return [
        SkillResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            category=s.category.value,
            source=s.source.value,
            version=s.version,
            enabled=s.enabled
        )
        for s in results
    ]

@router.get("/categories", response_model=List[SkillCategoryResponse])
async def get_categories():
    """获取技能分类列表"""
    return skill_registry.get_categories()

@router.get("/stats", response_model=SkillStatsResponse)
async def get_stats():
    """获取技能统计信息"""
    stats = skill_registry.get_stats()
    return SkillStatsResponse(**stats)

@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    """
    获取技能详情
    
    参数:
    - skill_id: 技能ID
    """
    skill = skill_registry.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail=f"技能 {skill_id} 不存在")
    
    return SkillResponse(
        id=skill.id,
        name=skill.name,
        description=skill.description,
        category=skill.category.value,
        source=skill.source.value,
        version=skill.version,
        enabled=skill.enabled
    )

@router.post("/{skill_id}/invoke", response_model=SkillInvokeResponse)
async def invoke_skill(skill_id: str, request: SkillInvokeRequest):
    """
    调用技能
    
    参数:
    - skill_id: 技能ID
    - request: 调用参数
    """
    skill = skill_registry.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail=f"技能 {skill_id} 不存在")
    
    if not skill.enabled:
        raise HTTPException(status_code=400, detail=f"技能 {skill_id} 未启用")
    
    # 根据技能类型执行不同操作
    try:
        result = await _execute_skill(skill, request.parameters)
        return SkillInvokeResponse(
            success=True,
            skill_id=skill_id,
            result=result,
            message=f"技能 {skill.name} 执行成功"
        )
    except Exception as e:
        return SkillInvokeResponse(
            success=False,
            skill_id=skill_id,
            result=None,
            message=f"执行失败: {str(e)}"
        )

async def _execute_skill(skill, parameters: Dict) -> Any:
    """执行技能"""
    # 这里根据技能类型调用不同的执行逻辑
    # 实际实现需要集成具体的技能工具
    
    if skill.category == SkillCategory.LITERATURE:
        return await _execute_literature_skill(skill, parameters)
    elif skill.category == SkillCategory.TRIAL:
        return await _execute_trial_skill(skill, parameters)
    elif skill.category == SkillCategory.BIOINFORMATICS:
        return await _execute_bioinformatics_skill(skill, parameters)
    elif skill.category == SkillCategory.DRUG:
        return await _execute_drug_skill(skill, parameters)
    else:
        return {"message": f"技能 {skill.name} 已准备就绪", "parameters": parameters}

async def _execute_literature_skill(skill, parameters: Dict) -> Any:
    """执行文献检索技能"""
    # 集成PubMed、文献挖掘等
    return {
        "skill": skill.name,
        "action": "literature_search",
        "query": parameters.get("query", ""),
        "results": "文献检索结果将在这里返回"
    }

async def _execute_trial_skill(skill, parameters: Dict) -> Any:
    """执行临床试验技能"""
    return {
        "skill": skill.name,
        "action": "clinical_trial",
        "disease": parameters.get("disease", ""),
        "results": "临床试验数据将在这里返回"
    }

async def _execute_bioinformatics_skill(skill, parameters: Dict) -> Any:
    """执行生物信息学技能"""
    return {
        "skill": skill.name,
        "action": "bioinformatics_analysis",
        "data_type": parameters.get("data_type", ""),
        "results": "生物信息学分析结果将在这里返回"
    }

async def _execute_drug_skill(skill, parameters: Dict) -> Any:
    """执行药物研发技能"""
    return {
        "skill": skill.name,
        "action": "drug_research",
        "drug_name": parameters.get("drug_name", ""),
        "results": "药物研发数据将在这里返回"
    }

# ============ 特色功能 ============

@router.get("/featured/recommended")
async def get_recommended_skills(
    context: Optional[str] = Query(None, description="使用场景上下文")
):
    """
    获取推荐技能
    
    根据上下文智能推荐相关技能
    """
    # 基础推荐：返回每个分类的热门技能
    recommended = []
    
    # 文献检索类
    lit_skills = skill_registry.get_skills_by_category(SkillCategory.LITERATURE)
    if lit_skills:
        recommended.append(lit_skills[0])
    
    # 临床试验类
    trial_skills = skill_registry.get_skills_by_category(SkillCategory.TRIAL)
    if trial_skills:
        recommended.append(trial_skills[0])
    
    # 生信分析类
    bio_skills = skill_registry.get_skills_by_category(SkillCategory.BIOINFORMATICS)
    if bio_skills:
        recommended.append(bio_skills[0])
    
    # 临床决策类
    clinical_skills = skill_registry.get_skills_by_category(SkillCategory.CLINICAL)
    if clinical_skills:
        recommended.append(clinical_skills[0])
    
    return [
        SkillResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            category=s.category.value,
            source=s.source.value,
            version=s.version,
            enabled=s.enabled
        )
        for s in recommended
    ]

@router.get("/featured/new")
async def get_new_skills():
    """获取最新添加的技能"""
    # 返回最近添加的技能
    all_skills = skill_registry.get_all_skills()
    # 按某种逻辑排序，这里简化处理
    new_skills = all_skills[-10:]  # 返回最后10个
    
    return [
        SkillResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            category=s.category.value,
            source=s.source.value,
            version=s.version,
            enabled=s.enabled
        )
        for s in new_skills
    ]

@router.get("/featured/popular")
async def get_popular_skills():
    """获取热门技能"""
    # 返回最常用的技能
    popular_ids = [
        "pubmed-search",
        "clinicaltrials-db",
        "literature-review",
        "clinical-decision",
        "trial-design",
        "drugbank",
        "bioinformatics-scrna"
    ]
    
    popular = []
    for sid in popular_ids:
        skill = skill_registry.get_skill(sid)
        if skill:
            popular.append(skill)
    
    return [
        SkillResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            category=s.category.value,
            source=s.source.value,
            version=s.version,
            enabled=s.enabled
        )
        for s in popular
    ]
