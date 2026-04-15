"""
分子生成主引擎
整合多种生成策略和优化器
"""

import logging
from dataclasses import dataclass, asdict
from typing import Optional

from .generators import SMILESGenerator, GeneratedMolecule
from .optimizer import MoleculeOptimizer

logger = logging.getLogger(__name__)


@dataclass
class GenerationReport:
    """分子生成报告"""
    target: str
    total_generated: int
    valid_molecules: int
    top_candidates: list[dict]
    method: str
    summary: str


class MolecularGenerationEngine:
    """
    分子生成引擎
    靶点信息 → 生成+优化 → 候选分子
    """

    def __init__(self, seed: int = 42):
        self.generator = SMILESGenerator(seed=seed)
        self.optimizer = MoleculeOptimizer()

    def generate_candidates(
        self,
        target_name: str = "",
        scaffold: Optional[str] = None,
        n_generate: int = 200,
        n_optimize: int = 50,
        target_properties: Optional[dict] = None,
        top_n: int = 20
    ) -> GenerationReport:
        """
        从头生成候选分子

        Args:
            target_name: 靶点名称
            scaffold: 起始骨架
            n_generate: 生成数量
            n_optimize: 优化迭代次数
            target_properties: 目标属性约束
            top_n: 返回Top N
        """
        logger.info(f"=== 开始分子生成: {target_name or 'de novo'} ===")

        # 默认目标属性
        props = target_properties or {
            "mw": 400,
            "logp": 2.5,
            "hbd": 2,
            "hba": 5,
        }

        # Step 1: 生成初始分子库
        logger.info("Step 1: 生成初始分子库...")
        generated = self.generator.generate(
            n_molecules=n_generate,
            target_properties=props,
            scaffold=scaffold
        )

        if not generated:
            return GenerationReport(
                target=target_name,
                total_generated=0,
                valid_molecules=0,
                top_candidates=[],
                method="de novo",
                summary="分子生成失败"
            )

        # Step 2: 优化Top候选
        logger.info("Step 2: 分子优化...")
        # 按QED排序取Top进行优化
        sorted_mols = sorted(generated, key=lambda m: m.qed, reverse=True)
        initial_population = [m.smiles for m in sorted_mols[:min(50, len(sorted_mols))]]

        if n_optimize > 0 and len(initial_population) > 5:
            optimized_population = self.optimizer.genetic_optimize(
                initial_population=initial_population,
                target_props=props,
            )
            all_smiles = list(set(
                [m.smiles for m in generated] + optimized_population
            ))
        else:
            all_smiles = [m.smiles for m in generated]

        # Step 3: 重新评估
        logger.info("Step 3: 重新评估...")
        candidates = []
        seen = set()
        for smiles in all_smiles:
            if smiles in seen:
                continue
            seen.add(smiles)

            valid, props_dict = self.generator._validate_and_properties(smiles)
            if valid:
                candidates.append({
                    "smiles": smiles,
                    **props_dict,
                })

        # 按QED排序
        candidates.sort(key=lambda c: c.get("qed", 0), reverse=True)
        top = candidates[:top_n]

        valid_count = len(candidates)
        return GenerationReport(
            target=target_name,
            total_generated=len(generated),
            valid_molecules=valid_count,
            top_candidates=top,
            method="de_novo_generation + genetic_optimization",
            summary=f"生成{len(generated)}个分子，{valid_count}个有效，Top {top_n}已选出"
        )

    def scaffold_hop(
        self,
        reference_smiles: str,
        n_variants: int = 50
    ) -> GenerationReport:
        """
        骨架跃迁：基于参考分子生成新骨架

        Args:
            reference_smiles: 参考分子SMILES
            n_variants: 生成变体数
        """
        logger.info(f"骨架跃迁: {reference_smiles[:50]}...")

        generated = self.generator.generate(
            n_molecules=n_variants,
            scaffold=None,  # 不用原始骨架，用片段重组
        )

        candidates = []
        for mol in generated:
            if mol.validity:
                candidates.append({
                    "smiles": mol.smiles,
                    "qed": mol.qed,
                    "sa_score": mol.sa_score,
                    "logp": mol.logp,
                    "mw": mol.mw,
                })

        return GenerationReport(
            target=f"scaffold_hop:{reference_smiles[:30]}",
            total_generated=len(generated),
            valid_molecules=len(candidates),
            top_candidates=candidates[:n_variants],
            method="scaffold_hopping",
            summary=f"骨架跃迁生成{len(candidates)}个新骨架"
        )
