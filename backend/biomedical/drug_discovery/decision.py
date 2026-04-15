"""
决策引擎
Go/No-Go智能决策，风险评估
"""

import logging
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


@dataclass
class DecisionResult:
    """决策结果"""
    decision: str           # GO / NO-GO / CONDITIONAL-GO
    confidence: float       # 0-1
    rationale: str
    risk_factors: list[str]
    conditions: list[str]   # CONDITIONAL-GO的条件


class DecisionEngine:
    """
    药物研发决策引擎
    基于多维数据的Go/No-Go判断
    """

    # Go/No-Go阈值
    GO_THRESHOLDS = {
        "min_activity": 6.0,       # pIC50
        "min_selectivity": 10,     # 倍数
        "max_herg_risk": 0.5,
        "min_oral_bioavailability": 0.2,
        "max_sa_score": 6.0,
    }

    def __init__(self, llm_client: Optional[OpenAI] = None, llm_model: str = "mimo-v2-pro"):
        self.llm = llm_client
        self.model = llm_model

    def evaluate_candidate(
        self,
        candidate_data: dict,
        stage: str = "lead"  # hit / lead / candidate
    ) -> DecisionResult:
        """
        评估单个候选分子

        Args:
            candidate_data: 候选分子数据
            stage: 开发阶段
        """
        scores = {}
        risks = []

        # 活性检查
        activity = candidate_data.get("activity", candidate_data.get("predicted_pkd", 0))
        if activity >= self.GO_THRESHOLDS["min_activity"]:
            scores["activity"] = min(activity / 9, 1.0)
        else:
            scores["activity"] = activity / 9
            risks.append(f"活性偏低 (pIC50={activity:.1f} < {self.GO_THRESHOLDS['min_activity']})")

        # ADMET检查
        admet = candidate_data.get("admet_score", 0.5)
        scores["admet"] = admet
        if admet < 0.4:
            risks.append(f"ADMET评分低 ({admet:.2f})")

        # hERG风险
        herg = candidate_data.get("herg_inhibition", candidate_data.get("herg_risk", 0.3))
        if herg > self.GO_THRESHOLDS["max_herg_risk"]:
            risks.append(f"hERG抑制风险高 ({herg:.2f})")

        # 合成可行性
        sa = candidate_data.get("sa_score", 4.0)
        if sa > self.GO_THRESHOLDS["max_sa_score"]:
            risks.append(f"合成难度高 (SA={sa:.1f})")

        # 综合评分
        total = (
            scores.get("activity", 0) * 0.35 +
            scores.get("admet", 0) * 0.35 +
            (1 - herg) * 0.15 +
            max(0, 1 - (sa - 1) / 9) * 0.15
        )

        # 决策
        if total > 0.7 and len(risks) <= 1:
            decision = "GO"
        elif total > 0.5 and len(risks) <= 2:
            decision = "CONDITIONAL-GO"
        else:
            decision = "NO-GO"

        return DecisionResult(
            decision=decision,
            confidence=round(total, 3),
            rationale=f"综合评分{total:.3f}，{len(risks)}个风险因素",
            risk_factors=risks,
            conditions=["需进一步ADMET验证"] if decision == "CONDITIONAL-GO" else []
        )

    def evaluate_portfolio(
        self,
        candidates: list[dict],
        max_select: int = 5
    ) -> dict:
        """
        评估候选组合，选出最佳开发组合
        """
        evaluations = []
        for c in candidates:
            result = self.evaluate_candidate(c)
            evaluations.append({
                "smiles": c.get("smiles", ""),
                "decision": result.decision,
                "confidence": result.confidence,
                "risks": result.risk_factors,
            })

        # 排序
        evaluations.sort(key=lambda e: e["confidence"], reverse=True)

        go_candidates = [e for e in evaluations if e["decision"] == "GO"][:max_select]
        conditional = [e for e in evaluations if e["decision"] == "CONDITIONAL-GO"][:max_select]

        return {
            "total_evaluated": len(evaluations),
            "go_count": len(go_candidates),
            "conditional_count": len(conditional),
            "nogo_count": len([e for e in evaluations if e["decision"] == "NO-GO"]),
            "top_candidates": go_candidates + conditional,
            "recommendation": self._portfolio_recommendation(go_candidates, conditional),
        }

    def _portfolio_recommendation(self, go: list, conditional: list) -> str:
        """组合建议"""
        if len(go) >= 3:
            return "优秀组合：多个GO候选，建议推进到先导优化阶段"
        elif len(go) >= 1:
            return f"良好：{len(go)}个GO候选，建议聚焦开发"
        elif len(conditional) >= 3:
            return f"中等：{len(conditional)}个条件GO，建议进一步优化后评估"
        else:
            return "需改进：候选质量不足，建议扩大筛选或调整策略"
