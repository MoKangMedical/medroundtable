"""
MedRoundTable 讨论质量评估 — Hermes改进
评估每次圆桌讨论的质量，确保科研讨论有产出

用户视角：临床研究者开完会，需要知道讨论质量如何、有什么产出
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class DiscussionQuality:
    """讨论质量评估"""
    session_id: str
    participation_score: float    # 参与度 0-1
    diversity_score: float        # 观点多样性 0-1
    evidence_score: float         # 证据引用率 0-1
    actionability_score: float    # 可操作性 0-1
    overall_score: float          # 综合评分 0-1
    strengths: List[str]          # 优势
    improvements: List[str]       # 改进建议
    output_summary: str           # 产出摘要


class QualityAssessor:
    """圆桌讨论质量评估器"""
    
    # 证据关键词
    EVIDENCE_KEYWORDS = ["文献", "研究", "数据", "p值", "CI", "OR", "HR", "RCT", "meta分析", "指南"]
    ACTION_KEYWORDS = ["建议", "方案", "下一步", "计划", "实施", "执行", "分配"]
    
    def assess(
        self,
        session_id: str,
        messages: List[Dict],
        agents_count: int = 14,
        expected_stages: int = 5
    ) -> DiscussionQuality:
        """
        评估讨论质量
        
        Args:
            session_id: 会话ID
            messages: 消息列表 [{"agent": "临床主任", "content": "...", "stage": "..."}]
            agents_count: 预期参与Agent数
            expected_stages: 预期讨论阶段数
        """
        if not messages:
            return DiscussionQuality(
                session_id=session_id,
                participation_score=0, diversity_score=0,
                evidence_score=0, actionability_score=0,
                overall_score=0, strengths=["无讨论记录"],
                improvements=["开始讨论"], output_summary="暂无"
            )
        
        total = len(messages)
        unique_agents = len(set(m.get("agent", "") for m in messages))
        unique_stages = len(set(m.get("stage", "") for m in messages))
        all_text = " ".join(m.get("content", "") for m in messages)
        
        # 参与度
        participation = min(unique_agents / max(agents_count * 0.3, 1), 1.0)
        
        # 多样性
        diversity = min(unique_stages / max(expected_stages * 0.6, 1), 1.0)
        
        # 证据引用率
        evidence_count = sum(1 for kw in self.EVIDENCE_KEYWORDS if kw in all_text)
        evidence = min(evidence_count / 5, 1.0)
        
        # 可操作性
        action_count = sum(1 for kw in self.ACTION_KEYWORDS if kw in all_text)
        actionability = min(action_count / 3, 1.0)
        
        # 综合评分
        overall = participation * 0.25 + diversity * 0.25 + evidence * 0.25 + actionability * 0.25
        
        # 优势和改进建议
        strengths = []
        improvements = []
        
        if participation > 0.7:
            strengths.append(f"{unique_agents}位专家积极参与")
        else:
            improvements.append(f"增加参与专家（当前{unique_agents}位，建议至少{int(agents_count*0.5)}位）")
        
        if evidence > 0.5:
            strengths.append("讨论引用了充分的文献证据")
        else:
            improvements.append("增加文献引用，增强讨论的循证基础")
        
        if actionability > 0.5:
            strengths.append("讨论产出了可操作的行动方案")
        else:
            improvements.append("在讨论结束时明确行动项和责任人")
        
        return DiscussionQuality(
            session_id=session_id,
            participation_score=round(participation, 2),
            diversity_score=round(diversity, 2),
            evidence_score=round(evidence, 2),
            actionability_score=round(actionability, 2),
            overall_score=round(overall, 2),
            strengths=strengths,
            improvements=improvements,
            output_summary=f"共{total}条消息，{unique_agents}位专家参与，{unique_stages}个阶段"
        )
    
    def format_report(self, quality: DiscussionQuality) -> str:
        """格式化评估报告"""
        score_emoji = "🟢" if quality.overall_score >= 0.7 else "🟡" if quality.overall_score >= 0.4 else "🔴"
        lines = [
            f"{score_emoji} 圆桌讨论质量评估",
            f"",
            f"📊 综合评分: {quality.overall_score:.0%}",
            f"  参与度: {'█' * int(quality.participation_score * 10)}{'░' * (10 - int(quality.participation_score * 10))} {quality.participation_score:.0%}",
            f"  多样性: {'█' * int(quality.diversity_score * 10)}{'░' * (10 - int(quality.diversity_score * 10))} {quality.diversity_score:.0%}",
            f"  证据度: {'█' * int(quality.evidence_score * 10)}{'░' * (10 - int(quality.evidence_score * 10))} {quality.evidence_score:.0%}",
            f"  可操作: {'█' * int(quality.actionability_score * 10)}{'░' * (10 - int(quality.actionability_score * 10))} {quality.actionability_score:.0%}",
        ]
        if quality.strengths:
            lines.append(f"\n✅ 优势:")
            for s in quality.strengths:
                lines.append(f"  • {s}")
        if quality.improvements:
            lines.append(f"\n💡 改进建议:")
            for i in quality.improvements:
                lines.append(f"  → {i}")
        return "\n".join(lines)


if __name__ == "__main__":
    assessor = QualityAssessor()
    test_messages = [
        {"agent": "临床主任", "content": "这个研究假设需要文献支持", "stage": "假设提出"},
        {"agent": "流行病学", "content": "我建议采用RCT设计，参考NEJM 2024年的研究", "stage": "研究设计"},
        {"agent": "统计专家", "content": "样本量需要200例，p<0.05，90%检验效能", "stage": "统计方案"},
        {"agent": "博士生", "content": "我负责文献综述和数据采集", "stage": "任务分配"},
    ]
    quality = assessor.assess("test-001", test_messages)
    print(assessor.format_report(quality))
