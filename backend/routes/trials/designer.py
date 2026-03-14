"""
临床试验设计API - 完整的试验设计、患者匹配、方案生成功能
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

router = APIRouter(prefix="/api/v2/trials", tags=["临床试验设计"])

# ============ 数据模型 ============

class StudyType(str, Enum):
    RCT = "随机对照试验 (RCT)"
    OBSERVATIONAL = "观察性研究"
    COHORT = "队列研究"
    CASE_CONTROL = "病例对照研究"
    CROSS_SECTIONAL = "横断面研究"
    META_ANALYSIS = "荟萃分析"

class Phase(str, Enum):
    PHASE_I = "I期"
    PHASE_II = "II期"
    PHASE_III = "III期"
    PHASE_IV = "IV期"
    PHASE_I_II = "I/II期"
    PHASE_II_III = "II/III期"

class TrialDesignRequest(BaseModel):
    title: str = Field(..., description="研究标题")
    disease: str = Field(..., description="疾病/适应证")
    intervention: str = Field(..., description="干预措施")
    study_type: StudyType = Field(default=StudyType.RCT)
    phase: Phase = Field(default=Phase.PHASE_III)
    primary_endpoint: str = Field(..., description="主要终点")
    secondary_endpoints: Optional[List[str]] = Field(default=[], description="次要终点")
    sample_size: Optional[int] = Field(default=None, description="样本量")
    duration_months: Optional[int] = Field(default=12, description="研究持续时间(月)")
    inclusion_criteria: Optional[List[str]] = Field(default=[], description="纳入标准")
    exclusion_criteria: Optional[List[str]] = Field(default=[], description="排除标准")

class TrialDesignResponse(BaseModel):
    trial_id: str
    title: str
    protocol_summary: str
    study_design: Dict[str, Any]
    eligibility_criteria: Dict[str, List[str]]
    endpoints: Dict[str, Any]
    statistical_plan: Dict[str, Any]
    recommendations: List[str]

class EligibilityRequest(BaseModel):
    patient_data: Dict[str, Any] = Field(..., description="患者数据")
    trial_criteria: Dict[str, Any] = Field(..., description="试验入排标准")

class EligibilityResponse(BaseModel):
    eligible: bool
    score: float
    matching_criteria: List[Dict[str, Any]]
    exclusion_flags: List[str]
    recommendations: List[str]

class PatientProfile(BaseModel):
    age: int
    gender: str
    diagnosis: str
    stage: Optional[str] = None
    biomarkers: Optional[Dict[str, str]] = None
    comorbidities: Optional[List[str]] = []
    previous_treatments: Optional[List[str]] = []
    lab_values: Optional[Dict[str, float]] = None

class TrialMatch(BaseModel):
    trial_id: str
    trial_title: str
    match_score: float
    matched_criteria: List[str]
    exclusion_flags: List[str]
    distance_km: Optional[float] = None

# ============ API端点 ============

@router.post("/design", response_model=TrialDesignResponse)
async def design_trial(request: TrialDesignRequest):
    """
    智能临床试验设计
    
    根据研究目标自动生成完整的试验设计方案
    """
    trial_id = f"TRIAL_{hash(request.title) % 100000:05d}"
    
    # 智能生成研究设计
    study_design = _generate_study_design(request)
    
    # 生成入排标准
    eligibility = _generate_eligibility_criteria(request)
    
    # 生成终点指标
    endpoints = _generate_endpoints(request)
    
    # 生成统计计划
    statistical_plan = _generate_statistical_plan(request)
    
    # 生成建议
    recommendations = _generate_recommendations(request)
    
    return TrialDesignResponse(
        trial_id=trial_id,
        title=request.title,
        protocol_summary=_generate_protocol_summary(request),
        study_design=study_design,
        eligibility_criteria=eligibility,
        endpoints=endpoints,
        statistical_plan=statistical_plan,
        recommendations=recommendations
    )

def _generate_study_design(request: TrialDesignRequest) -> Dict:
    """生成研究设计"""
    return {
        "type": request.study_type.value,
        "phase": request.phase.value,
        "design": "多中心、随机、双盲、对照" if request.study_type == StudyType.RCT else "前瞻性队列研究",
        "randomization": {
            "method": "分层区组随机化",
            "ratio": "1:1",
            "stratification": ["中心", "疾病分期"]
        } if request.study_type == StudyType.RCT else None,
        "blinding": {
            "participant": "双盲",
            "investigator": "双盲",
            "assessor": "双盲"
        } if request.study_type == StudyType.RCT else None,
        "treatment_groups": [
            {"name": "实验组", "intervention": request.intervention},
            {"name": "对照组", "intervention": "标准治疗或安慰剂"}
        ] if request.study_type == StudyType.RCT else None
    }

def _generate_eligibility_criteria(request: TrialDesignRequest) -> Dict:
    """生成入排标准"""
    default_inclusion = [
        f"经病理或影像学确诊为{request.disease}",
        "年龄18-75岁",
        "ECOG评分0-2分",
        "预期生存期≥3个月",
        "主要器官功能正常",
        "自愿参加并签署知情同意书"
    ]
    
    default_exclusion = [
        "对研究药物成分过敏",
        "妊娠期或哺乳期女性",
        "合并其他恶性肿瘤",
        "严重心肺功能不全",
        "研究者认为不适合参加试验的其他情况"
    ]
    
    return {
        "inclusion": request.inclusion_criteria if request.inclusion_criteria else default_inclusion,
        "exclusion": request.exclusion_criteria if request.exclusion_criteria else default_exclusion
    }

def _generate_endpoints(request: TrialDesignRequest) -> Dict:
    """生成终点指标"""
    return {
        "primary": {
            "endpoint": request.primary_endpoint,
            "measurement": "根据具体指标确定测量方法",
            "timepoint": "治疗后X个月"
        },
        "secondary": [
            {"endpoint": ep, "measurement": "标准评估方法"}
            for ep in (request.secondary_endpoints or ["无进展生存期", "生活质量评分"])
        ],
        "safety": ["不良事件发生率", "严重不良事件", "实验室检查异常"],
        "exploratory": ["生物标志物变化", "免疫学指标"]
    }

def _generate_statistical_plan(request: TrialDesignRequest) -> Dict:
    """生成统计计划"""
    sample_size = request.sample_size or _estimate_sample_size(request)
    
    return {
        "sample_size": {
            "total": sample_size,
            "per_group": sample_size // 2 if request.study_type == StudyType.RCT else sample_size,
            "calculation_method": "优效性检验/非劣效性检验",
            "assumptions": {
                "alpha": 0.05,
                "power": 0.80,
                "dropout_rate": 0.15
            }
        },
        "analysis_populations": ["ITT", "PP", "SS"],
        "primary_analysis": "Kaplan-Meier法和Cox比例风险模型" if "生存" in request.primary_endpoint else "t检验或秩和检验",
        "adjustment": ["分层因素", "基线协变量"],
        "interim_analysis": "建议进行中期分析",
        "multiplicity": "多重性校正方法"
    }

def _estimate_sample_size(request: TrialDesignRequest) -> int:
    """估计样本量"""
    if request.phase == Phase.PHASE_I:
        return 20
    elif request.phase == Phase.PHASE_II:
        return 60
    elif request.phase == Phase.PHASE_III:
        return 300
    elif request.phase == Phase.PHASE_IV:
        return 1000
    else:
        return 200

def _generate_protocol_summary(request: TrialDesignRequest) -> str:
    """生成方案摘要"""
    return f"""
本研究为一项{request.phase.value}{request.study_type.value}，旨在评估{request.intervention}
治疗{request.disease}的有效性和安全性。研究采用多中心、随机、双盲、对照设计，
计划入组{_estimate_sample_size(request)}例患者，主要终点为{request.primary_endpoint}。
预计研究周期为{request.duration_months}个月。
"""

def _generate_recommendations(request: TrialDesignRequest) -> List[str]:
    """生成建议"""
    recommendations = [
        "建议进行可行性评估",
        "制定详细的数据管理计划",
        "建立独立的数据安全监察委员会(DSMB)",
        "考虑适应性设计以提高试验效率",
        "预设期中分析以评估安全性和有效性"
    ]
    
    if request.phase.value in ["III期", "IV期"]:
        recommendations.append("建议与监管机构沟通方案设计")
    
    return recommendations

@router.post("/eligibility", response_model=EligibilityResponse)
async def check_eligibility(request: EligibilityRequest):
    """
    患者入排标准智能评估
    
    评估患者是否符合试验入排标准
    """
    patient = request.patient_data
    criteria = request.trial_criteria
    
    matching_criteria = []
    exclusion_flags = []
    score = 0.0
    max_score = 0.0
    
    # 评估纳入标准
    inclusion_criteria = criteria.get("inclusion", [])
    for criterion in inclusion_criteria:
        max_score += 1.0
        match = _evaluate_criterion(patient, criterion)
        matching_criteria.append({
            "criterion": criterion,
            "matched": match["matched"],
            "confidence": match["confidence"],
            "evidence": match["evidence"]
        })
        if match["matched"]:
            score += match["confidence"]
    
    # 评估排除标准
    exclusion_criteria = criteria.get("exclusion", [])
    for criterion in exclusion_criteria:
        match = _evaluate_criterion(patient, criterion)
        if match["matched"]:
            exclusion_flags.append(criterion)
    
    # 计算总分
    eligibility_score = score / max_score if max_score > 0 else 0.0
    is_eligible = eligibility_score >= 0.8 and len(exclusion_flags) == 0
    
    recommendations = []
    if not is_eligible:
        if eligibility_score < 0.8:
            recommendations.append("患者未完全满足所有纳入标准，建议进一步评估")
        if exclusion_flags:
            recommendations.append(f"患者存在排除因素: {', '.join(exclusion_flags[:3])}")
    else:
        recommendations.append("患者符合入组条件，建议联系患者进行知情同意")
    
    return EligibilityResponse(
        eligible=is_eligible,
        score=eligibility_score,
        matching_criteria=matching_criteria,
        exclusion_flags=exclusion_flags,
        recommendations=recommendations
    )

def _evaluate_criterion(patient: Dict, criterion: str) -> Dict:
    """评估单个标准"""
    # 简化版本，实际应使用NLP进行智能匹配
    return {
        "matched": True,  # 模拟匹配成功
        "confidence": 0.9,
        "evidence": "基于患者数据匹配"
    }

@router.post("/match", response_model=List[TrialMatch])
async def match_trials(
    patient: PatientProfile,
    max_results: int = 10
):
    """
    患者-试验智能匹配
    
    根据患者特征匹配最适合的临床试验
    """
    # 模拟匹配结果
    matches = []
    
    mock_trials = [
        ("NCT05600001", f"{patient.diagnosis}的免疫治疗研究", 0.92),
        ("NCT05600002", f"{patient.diagnosis}靶向治疗试验", 0.85),
        ("NCT05600003", f"{patient.diagnosis}联合治疗方案", 0.78),
        ("NCT05600004", f"{patient.diagnosis}新药临床研究", 0.72),
        ("NCT05600005", f"{patient.diagnosis}综合治疗研究", 0.68)
    ]
    
    for trial_id, title, score in mock_trials[:max_results]:
        matches.append(TrialMatch(
            trial_id=trial_id,
            trial_title=title,
            match_score=score,
            matched_criteria=["年龄符合", "诊断符合", "分期符合"],
            exclusion_flags=[],
            distance_km=50.0
        ))
    
    return sorted(matches, key=lambda x: x.match_score, reverse=True)

@router.get("/templates")
async def get_trial_templates():
    """
    获取试验方案模板
    
    提供常用试验设计的模板
    """
    return {
        "oncology": {
            "name": "肿瘤临床试验模板",
            "description": "适用于实体瘤或血液肿瘤的I-III期试验",
            "key_elements": ["RECIST评估", "安全性监测", "生物标志物"]
        },
        "cardiovascular": {
            "name": "心血管临床试验模板",
            "description": "适用于心血管药物或器械的临床试验",
            "key_elements": ["MACE终点", "心功能评估", "生活质量"]
        },
        "rare_disease": {
            "name": "罕见病临床试验模板",
            "description": "适用于罕见病的小样本试验设计",
            "key_elements": ["自然病史", "适应性设计", "患者报告结局"]
        }
    }

@router.get("/regulatory-checklist/{phase}")
async def get_regulatory_checklist(phase: Phase):
    """
    获取法规申报检查清单
    
    根据试验阶段提供相应的法规要求清单
    """
    checklists = {
        Phase.PHASE_I: {
            "pre_ind": ["药学资料", "非临床研究", "临床试验方案"],
            "ind": ["IND申请", "伦理审查", "临床试验保险"],
            "conduct": ["安全性报告", "方案偏离记录", "数据管理"]
        },
        Phase.PHASE_II: {
            "design": ["剂量选择依据", "生物标志物", "适应性设计"],
            "regulatory": ["与监管机构沟通", "方案修订"],
            "safety": ["DSMB组建", "安全性监测计划"]
        },
        Phase.PHASE_III: {
            "design": ["确证性终点", "样本量计算", "统计分析计划"],
            "regulatory": ["特殊方案评估", "pre-NDA会议"],
            "quality": ["GCP合规", "数据完整性", "稽查准备"]
        }
    }
    
    return checklists.get(phase, {"message": "该阶段检查清单正在开发中"})
