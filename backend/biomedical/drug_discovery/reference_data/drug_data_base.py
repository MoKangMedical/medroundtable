"""
肿瘤药物基础数据结构 + 通用查询接口
所有数据模块共享的基类
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class OncologyDrug:
    """肿瘤药物完整记录"""
    drug_name_cn: str           # 中文通用名
    drug_name_en: str           # 英文通用名
    brand_name: str             # 商品名
    drug_type: str              # 靶向/化疗/免疫/ADC/激素/细胞治疗/抗血管/其他
    subtype: str                # 细分子类(如TKI/mAb/PD-1/铂类等)
    mechanism: str              # 作用机制描述
    targets: list[str]          # 靶点基因符号列表
    approved_cancer_types: list[str]  # 批准适应癌种
    biomarkers: list[str]       # 伴随诊断标志物
    approval_fda: bool          # FDA批准
    approval_nmpa: bool         # NMPA批准
    approval_ema: bool          # EMA批准
    year_first_approved: int    # 首次批准年份
    manufacturer: str           # 主要生产企业
    smiles: str                 # SMILES (小分子) 或 "N/A" (大分子)
    molecular_formula: str      # 分子式
    cas_number: str             # CAS号
    route: str                  # 给药途径 (PO/IV/SC)
    common_adverse: list[str]   # 常见不良反应
    drug_interactions: list[str] # 主要药物相互作用
    clinical_trial_ids: list[str]  # 关联NCT号
    resistance_mechanisms: list[str]  # 已知耐药机制
    nccn_category: str          # NCCN推荐等级
    is_combination_component: bool  # 是否联合方案组成部分
    is_maintained: bool         # 是否可用于维持治疗
    is_orphan: bool             # 孤儿药
    notes: str                  # 备注


@dataclass
class TreatmentRegimen:
    """治疗方案"""
    regimen_name: str           # 方案名称
    drugs: list[str]            # 药物名称列表
    cancer_type: str            # 癌种
    line_of_therapy: str        # 一线/二线/三线/维持/辅助/新辅助
    molecular_subtype: str      # 分子亚型
    biomarker_required: str     # 需要的生物标志物
    cycle: str                  # 周期描述
    duration: str               # 推荐疗程
    evidence_level: str         # 1A/1B/2A/2B/3
    category: str               # 首选/可选/条件推荐
    notes: str                  # 特别说明


@dataclass
class CancerGuideline:
    """癌种治疗指南"""
    cancer_type: str
    icd10_code: str
    incidence_china: str        # 中国发病率
    five_year_survival: str     # 5年生存率
    molecular_testing: list[str] # 推荐分子检测
    first_line: list[TreatmentRegimen]
    second_line: list[TreatmentRegimen]
    third_line: list[TreatmentRegimen]
    maintenance: list[TreatmentRegimen]
    adjuvant: list[TreatmentRegimen]
    neoadjuvant: list[TreatmentRegimen]
    targeted_therapy_map: dict  # {靶点: [药物列表]}
    immunotherapy_eligibility: dict  # {PD-L1/MSI条件: 推荐方案}
    key_references: list[str]


# ============================================================
# 快速查询函数
# ============================================================

def search_by_target(drugs: list[OncologyDrug], target: str) -> list[OncologyDrug]:
    """按靶点搜索药物"""
    target_upper = target.upper()
    return [d for d in drugs if any(t.upper() == target_upper for t in d.targets)]

def search_by_cancer(drugs: list[OncologyDrug], cancer: str) -> list[OncologyDrug]:
    """按癌种搜索药物"""
    return [d for d in drugs if any(cancer in c for c in d.approved_cancer_types)]

def search_by_biomarker(drugs: list[OncologyDrug], biomarker: str) -> list[OncologyDrug]:
    """按生物标志物搜索药物"""
    return [d for d in drugs if any(biomarker in b for b in d.biomarkers)]

def search_by_type(drugs: list[OncologyDrug], drug_type: str) -> list[OncologyDrug]:
    """按药物类型搜索"""
    return [d for d in drugs if d.drug_type == drug_type]

def search_by_name(drugs: list[OncologyDrug], keyword: str) -> list[OncologyDrug]:
    """按名称模糊搜索"""
    kw = keyword.lower()
    return [d for d in drugs if kw in d.drug_name_cn.lower() or kw in d.drug_name_en.lower() or kw in d.brand_name.lower()]

def get_statistics(drugs: list[OncologyDrug]) -> dict:
    """统计概览"""
    from collections import Counter
    types = Counter(d.drug_type for d in drugs)
    subtypes = Counter(d.subtype for d in drugs)
    fda_approved = sum(1 for d in drugs if d.approval_fda)
    nmpa_approved = sum(1 for d in drugs if d.approval_nmpa)
    all_targets = set()
    all_cancers = set()
    for d in drugs:
        all_targets.update(d.targets)
        all_cancers.update(d.approved_cancer_types)
    return {
        "total_drugs": len(drugs),
        "fda_approved": fda_approved,
        "nmpa_approved": nmpa_approved,
        "by_type": dict(types),
        "by_subtype": dict(subtypes),
        "unique_targets": len(all_targets),
        "unique_cancer_types": len(all_cancers),
        "target_list": sorted(all_targets),
        "cancer_type_list": sorted(all_cancers),
    }
