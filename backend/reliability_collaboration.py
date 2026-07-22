"""Inference-time reliability routing for multi-agent research discussions.

This module adapts the useful runtime ideas described by MMedAgent-RL without
claiming to reproduce its reinforcement-learning training procedure.  It turns
structured expert opinions into an auditable disagreement profile and a
deterministic review route before a research plan can become a local job.
"""

from __future__ import annotations

import re
from collections import Counter
from statistics import mean
from typing import Any, Dict, List, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/v1/collaboration", tags=["collaboration-reliability"])


class ExpertOpinion(BaseModel):
    agent_id: str = Field(min_length=1, max_length=80)
    specialty: str = Field(min_length=1, max_length=120)
    conclusion: str = Field(min_length=1, max_length=1200)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_items: List[str] = Field(default_factory=list, max_length=12)
    uncertainties: List[str] = Field(default_factory=list, max_length=12)


class ReliabilityAssessmentRequest(BaseModel):
    case_id: str = Field(min_length=1, max_length=120)
    task_type: Literal[
        "research_question",
        "analysis_plan",
        "result_interpretation",
        "manuscript_claim",
    ] = "analysis_plan"
    question: str = Field(min_length=1, max_length=3000)
    opinions: List[ExpertOpinion] = Field(min_length=2, max_length=14)


def _normalise_conclusion(value: str) -> str:
    value = value.casefold().strip()
    value = re.sub(r"[\s\W_]+", "", value, flags=re.UNICODE)
    return value


def _evidence_strength(opinion: ExpertOpinion) -> float:
    """A transparent proxy, not a judgement of scientific truth."""
    citation_component = min(len(opinion.evidence_items), 3) / 3
    uncertainty_component = 1.0 if opinion.uncertainties else 0.0
    return round(0.85 * citation_component + 0.15 * uncertainty_component, 3)


def assess_reliability(request: ReliabilityAssessmentRequest) -> Dict[str, Any]:
    opinions = request.opinions
    keys = [_normalise_conclusion(opinion.conclusion) for opinion in opinions]
    counts = Counter(keys)
    majority_key, majority_count = counts.most_common(1)[0]
    majority_indices = [index for index, key in enumerate(keys) if key == majority_key]
    dissent_indices = [index for index, key in enumerate(keys) if key != majority_key]

    confidence_values = [opinion.confidence for opinion in opinions]
    evidence_values = [_evidence_strength(opinion) for opinion in opinions]
    consensus_ratio = majority_count / len(opinions)
    confidence_spread = max(confidence_values) - min(confidence_values)
    evidence_coverage = mean(evidence_values)
    majority_evidence = mean(evidence_values[index] for index in majority_indices)
    dissent_evidence = (
        max(evidence_values[index] for index in dissent_indices)
        if dissent_indices
        else 0.0
    )

    risk_flags: List[Dict[str, str]] = []
    consensus_without_evidence = consensus_ratio >= 0.8 and evidence_coverage < 0.45
    if consensus_without_evidence:
        risk_flags.append(
            {
                "code": "consensus_without_evidence",
                "severity": "high",
                "message": "多数意见缺少足够证据锚点；一致不等于正确。",
            }
        )

    minority_with_stronger_evidence = bool(
        dissent_indices and dissent_evidence > majority_evidence + 0.20
    )
    if minority_with_stronger_evidence:
        risk_flags.append(
            {
                "code": "minority_with_stronger_evidence",
                "severity": "high",
                "message": "少数意见的证据强度高于多数意见，需要独立仲裁。",
            }
        )

    if confidence_spread > 0.45:
        risk_flags.append(
            {
                "code": "confidence_dispersion",
                "severity": "medium",
                "message": "专家置信度离散较大，当前结论稳定性不足。",
            }
        )

    if mean(confidence_values) >= 0.8 and evidence_coverage < 0.55:
        risk_flags.append(
            {
                "code": "overconfident_low_evidence",
                "severity": "high",
                "message": "整体置信度高，但可追溯证据不足。",
            }
        )

    hard_route = (
        consensus_ratio < 0.5
        or consensus_without_evidence
        or minority_with_stronger_evidence
        or confidence_spread > 0.45
    )
    medium_route = consensus_ratio < 0.8 or evidence_coverage < 0.67 or confidence_spread > 0.25

    if hard_route:
        tier = "hard"
        label = "Hard · 独立复核"
        route = "independent_reanalysis"
        exploration_budget = "high"
        signing_allowed = False
        required_actions = [
            "隐去已有多数意见，由独立审查 Agent 重做一次分析",
            "逐条对照数据字段、代码输出或文献证据",
            "由人类研究负责人确认后才允许签名 local-job",
        ]
    elif medium_route:
        tier = "medium"
        label = "Medium · 冲突仲裁"
        route = "adjudicate_disagreement"
        exploration_budget = "medium"
        signing_allowed = False
        required_actions = [
            "让多数与少数意见各自提交最强反证",
            "由方法学审查 Agent 比较证据强度与数据可执行性",
            "仲裁记录写入审计链后再重新评估",
        ]
    else:
        tier = "easy"
        label = "Easy · 可汇总"
        route = "consolidate_with_verification"
        exploration_budget = "low"
        signing_allowed = True
        required_actions = [
            "汇总共识结论并保留每条证据来源",
            "执行一次基本字段与方法验证",
            "将少数不确定性保留到研究计划",
        ]

    majority_opinion = opinions[majority_indices[0]]
    dissenters = [
        {
            "agent_id": opinions[index].agent_id,
            "specialty": opinions[index].specialty,
            "conclusion": opinions[index].conclusion,
            "confidence": opinions[index].confidence,
            "evidence_strength": evidence_values[index],
        }
        for index in dissent_indices
    ]

    return {
        "case_id": request.case_id,
        "task_type": request.task_type,
        "protocol_version": "mrt-reliability-1.0",
        "training_mode": "inference-policy-only",
        "metrics": {
            "consensus_ratio": round(consensus_ratio, 3),
            "mean_confidence": round(mean(confidence_values), 3),
            "confidence_spread": round(confidence_spread, 3),
            "evidence_coverage": round(evidence_coverage, 3),
            "opinion_count": len(opinions),
        },
        "consensus": {
            "conclusion": majority_opinion.conclusion,
            "supporting_agents": [opinions[index].agent_id for index in majority_indices],
            "dissenters": dissenters,
        },
        "reliability_tier": {
            "code": tier,
            "label": label,
            "description": {
                "easy": "意见、证据与置信度较为一致，仍需基本验证。",
                "medium": "存在可解释的冲突，需要结构化仲裁。",
                "hard": "存在错误共识或强反证风险，需独立重分析与人工门禁。",
            }[tier],
        },
        "policy": {
            "route": route,
            "exploration_budget": exploration_budget,
            "signing_allowed": signing_allowed,
            "required_actions": required_actions,
        },
        "risk_flags": risk_flags,
        "audit": {
            "checks": [
                "多数意见与少数意见均已保留",
                "置信度与证据强度已分开计算",
                "评估结果不等同于医学真实性判定",
                "非 Easy 任务默认禁止自动签名下发",
            ]
        },
    }


@router.get("/protocol")
async def get_protocol() -> Dict[str, Any]:
    return {
        "name": "MedRoundTable Reliability Collaboration",
        "version": "1.0.0",
        "training_mode": "inference-policy-only",
        "topology": ["triage", "independent_specialists", "attending", "claim_verifier"],
        "tiers": ["easy", "medium", "hard"],
        "local_job_gate": "only_easy_can_auto_sign",
        "limitations": [
            "未复现 MMedAgent-RL 的强化学习训练",
            "可靠性分数是透明的运行时路由信号，不是临床准确率",
            "不用于自动诊断、治疗或患者级决策",
        ],
        "inspiration": {
            "paper": "MMedAgent-RL: Optimizing Multi-Agent Collaboration for Multimodal Medical Reasoning",
            "url": "https://arxiv.org/abs/2506.00555",
        },
    }


@router.post("/assess")
async def assess(request: ReliabilityAssessmentRequest) -> Dict[str, Any]:
    return assess_reliability(request)
