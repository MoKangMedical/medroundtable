"""
先导优化主引擎
整合多参数优化和分子编辑操作
"""

import logging
from dataclasses import dataclass, asdict
from typing import Optional

from admet_prediction.engine import ADMETEngine
from molecular_generation.optimizer import MoleculeOptimizer

logger = logging.getLogger(__name__)


@dataclass
class LeadCandidate:
    """先导化合物候选"""
    smiles: str
    activity_score: float
    admet_score: float
    synthesis_score: float
    composite_score: float
    generation: int
    changes: list[str]


class LeadOptimizationEngine:
    """
    先导优化引擎
    hit → lead → candidate 的优化流水线
    """

    def __init__(self):
        self.admet = ADMETEngine()
        self.optimizer = MoleculeOptimizer()

    def optimize(
        self,
        starting_smiles: str,
        objective_weights: Optional[dict] = None,
        max_generations: int = 20,
        population_size: int = 30
    ) -> dict:
        """
        先导优化流程

        Args:
            starting_smiles: 起始hit分子
            objective_weights: 各目标权重 {activity, admet, synthesis}
            max_generations: 最大优化代数
            population_size: 种群大小
        """
        weights = objective_weights or {
            "activity": 0.40,
            "admet": 0.35,
            "synthesis": 0.25
        }

        logger.info(f"=== 开始先导优化: {starting_smiles[:50]} ===")

        # 初始ADMET评估
        initial_report = self.admet.predict(starting_smiles)
        initial_score = initial_report.overall["total_score"]

        logger.info(f"初始ADMET评分: {initial_score}")

        # 复合评分函数
        def composite_score(smiles: str) -> float:
            try:
                report = self.admet.predict(smiles)
                admet_score = report.overall["total_score"]

                # 合成可及性
                sa_score = 1.0 - (report.synthesis["sa_score"] - 1) / 9

                # 活性估计（基于与起始分子的相似性）
                activity = self._estimate_activity(smiles, starting_smiles)

                total = (
                    activity * weights["activity"] +
                    admet_score * weights["admet"] +
                    max(0, sa_score) * weights["synthesis"]
                )
                return total
            except:
                return 0.0

        # 设置评分函数
        self.optimizer.scoring_fn = composite_score

        # 运行优化
        results = self.optimizer.optimize(
            smiles=starting_smiles,
            n_iterations=max_generations * population_size
        )

        # 收集候选
        candidates = []
        current_smiles = starting_smiles
        for i, result in enumerate(results):
            opt_smiles = result.optimized_smiles
            report = self.admet.predict(opt_smiles)

            candidate = LeadCandidate(
                smiles=opt_smiles,
                activity_score=self._estimate_activity(opt_smiles, starting_smiles),
                admet_score=report.overall["total_score"],
                synthesis_score=1.0 - (report.synthesis["sa_score"] - 1) / 9,
                composite_score=composite_score(opt_smiles),
                generation=result.generation,
                changes=[f"score_delta: {result.improvements.get('score_delta', 0)}"]
            )
            candidates.append(candidate)

        # 排序
        candidates.sort(key=lambda c: c.composite_score, reverse=True)

        return {
            "starting_smiles": starting_smiles,
            "initial_admet": asdict(initial_report),
            "candidates_found": len(candidates),
            "top_candidates": [asdict(c) for c in candidates[:10]],
            "optimization_trajectory": [
                {
                    "generation": c.generation,
                    "composite_score": c.composite_score,
                    "smiles": c.smiles
                }
                for c in candidates[:20]
            ],
            "weights_used": weights,
        }

    def multi_param_balance(
        self,
        smiles_list: list[str],
        activity_values: Optional[list[float]] = None
    ) -> list[dict]:
        """
        多参数平衡评估
        对多个分子进行ADMET+活性+合成的综合评估
        """
        results = []
        for i, smiles in enumerate(smiles_list):
            try:
                report = self.admet.predict(smiles)
                activity = activity_values[i] if activity_values and i < len(activity_values) else 0.5

                sa_score = report.synthesis["sa_score"]
                sa_normalized = max(0, 1 - (sa_score - 1) / 9)

                composite = (
                    activity * 0.40 +
                    report.overall["total_score"] * 0.35 +
                    sa_normalized * 0.25
                )

                results.append({
                    "smiles": smiles,
                    "activity": round(activity, 3),
                    "admet_score": report.overall["total_score"],
                    "sa_score": sa_score,
                    "sa_normalized": round(sa_normalized, 3),
                    "composite_score": round(composite, 3),
                    "pass_filter": report.pass_filter,
                    "recommendation": report.recommendation,
                })
            except Exception as e:
                logger.warning(f"评估失败 ({smiles[:30]}): {e}")

        results.sort(key=lambda r: r["composite_score"], reverse=True)
        return results

    def _estimate_activity(self, smiles: str, reference: str) -> float:
        """
        基于分子相似性的活性估计
        使用Tanimoto相似性（简化版）
        """
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem, DataStructs

            mol1 = Chem.MolFromSmiles(smiles)
            mol2 = Chem.MolFromSmiles(reference)

            if mol1 and mol2:
                fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2)
                fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2)
                similarity = DataStructs.TanimotoSimilarity(fp1, fp2)
                return round(similarity, 3)
        except:
            pass

        # 简化相似性：公共子串比例
        common = len(set(smiles) & set(reference))
        total = len(set(smiles) | set(reference))
        return round(common / max(total, 1), 3)
