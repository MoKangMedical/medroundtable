"""
DMTA循环管理器
Design → Make → Test → Analyze 的自动化循环
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class DMTACycle:
    """单次DMTA循环"""
    cycle_id: int
    design_candidates: list[dict] = field(default_factory=list)
    make_molecules: list[dict] = field(default_factory=list)
    test_results: list[dict] = field(default_factory=list)
    analysis_summary: str = ""
    go_decision: bool = False
    timestamp: str = ""


class DMTAManager:
    """
    DMTA循环管理器
    自动化Design-Make-Test-Analyze迭代
    """

    def __init__(self, max_cycles: int = 5):
        self.max_cycles = max_cycles
        self.cycles: list[DMTACycle] = []
        self.current_cycle = 0

    def start_cycle(self) -> DMTACycle:
        """开始新的DMTA循环"""
        self.current_cycle += 1
        cycle = DMTACycle(
            cycle_id=self.current_cycle,
            timestamp=datetime.now().isoformat()
        )
        self.cycles.append(cycle)
        logger.info(f"🔄 DMTA循环 #{self.current_cycle} 开始")
        return cycle

    def design_phase(self, candidates: list[dict]) -> list[dict]:
        """
        Design阶段：选择要合成的分子
        基于ADMET+活性+合成可行性的综合评分
        """
        if not self.cycles:
            self.start_cycle()

        cycle = self.cycles[-1]
        cycle.design_candidates = candidates

        # 选择策略：平衡多样性与质量
        selected = self._select_for_synthesis(candidates)
        logger.info(f"  📐 Design: {len(candidates)}候选 → {len(selected)}选定合成")
        return selected

    def make_phase(self, molecules: list[dict]) -> list[dict]:
        """
        Make阶段：标记为待合成
        （实际合成需实验，这里记录计划）
        """
        cycle = self.cycles[-1]
        for mol in molecules:
            mol["synthesis_status"] = "planned"
            mol["planned_date"] = datetime.now().isoformat()

        cycle.make_molecules = molecules
        logger.info(f"  🧪 Make: {len(molecules)}个分子列入合成计划")
        return molecules

    def test_phase(self, test_data: list[dict]) -> list[dict]:
        """
        Test阶段：记录实验测试结果
        """
        cycle = self.cycles[-1]
        cycle.test_results = test_data
        logger.info(f"  🔬 Test: {len(test_data)}个测试结果")
        return test_data

    def analyze_phase(self) -> dict:
        """
        Analyze阶段：分析测试结果，决定下一步
        """
        cycle = self.cycles[-1]

        # 统计
        n_tested = len(cycle.test_results)
        n_active = sum(1 for t in cycle.test_results if t.get("activity", 0) > 6.0)
        n_pass_admet = sum(1 for t in cycle.test_results if t.get("admet_pass", False))

        # Go/No-Go决策
        go = n_active > 0 and n_pass_admet > 0
        cycle.go_decision = go

        summary = (f"循环#{cycle.cycle_id}: 测试{n_tested}个, "
                   f"活性{n_active}个, ADMET通过{n_pass_admet}个 → "
                   f"{'GO' if go else 'NO-GO'}")
        cycle.analysis_summary = summary

        logger.info(f"  📊 Analyze: {summary}")

        return {
            "cycle_id": cycle.cycle_id,
            "n_tested": n_tested,
            "n_active": n_active,
            "n_pass_admet": n_pass_admet,
            "go_decision": go,
            "summary": summary,
            "next_steps": self._recommend_next(go, cycle),
        }

    def _select_for_synthesis(self, candidates: list[dict], max_select: int = 10) -> list[dict]:
        """选择待合成分子（多样性+质量平衡）"""
        # 按综合分排序
        sorted_cands = sorted(
            candidates,
            key=lambda c: c.get("composite_score", c.get("qed", 0)),
            reverse=True
        )

        selected = []
        seen_scaffolds = set()

        for cand in sorted_cands:
            if len(selected) >= max_select:
                break

            # 简化骨架检查
            scaffold = cand.get("smiles", "")[:10]
            if scaffold not in seen_scaffolds:
                selected.append(cand)
                seen_scaffolds.add(scaffold)

        return selected

    def _recommend_next(self, go: bool, cycle: DMTACycle) -> list[str]:
        """推荐下一步行动"""
        if go:
            return [
                "对活性化合物进行先导优化",
                "扩大合成类似物",
                "进行更详细的ADMET表征",
                "评估体内PK"
            ]
        else:
            return [
                "重新审视靶点假设",
                "扩大化合物库筛选",
                "尝试不同的化学骨架",
                "考虑骨架跃迁策略"
            ]

    def get_progress_report(self) -> dict:
        """获取DMTA进度报告"""
        return {
            "total_cycles": len(self.cycles),
            "current_cycle": self.current_cycle,
            "cycles": [
                {
                    "id": c.cycle_id,
                    "designed": len(c.design_candidates),
                    "made": len(c.make_molecules),
                    "tested": len(c.test_results),
                    "go": c.go_decision,
                    "summary": c.analysis_summary,
                }
                for c in self.cycles
            ],
            "overall_progress": f"{self.current_cycle}/{self.max_cycles} 循环"
        }
