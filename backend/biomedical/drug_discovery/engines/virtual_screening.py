"""
虚拟筛选主引擎
整合化合物库、分子对接、亲和力评分，输出Top候选化合物
"""

import logging
from dataclasses import dataclass, asdict
from typing import Optional

from .compound_library import CompoundLibrary, Compound
from .docking import DockingEngine
from .scorer import AffinityScorer

logger = logging.getLogger(__name__)


@dataclass
class ScreeningResult:
    """虚拟筛选结果"""
    target: str
    total_screened: int
    hits_found: int
    top_candidates: list[dict]
    method: str
    summary: str


class VirtualScreeningEngine:
    """
    虚拟筛选引擎
    靶点 + 化合物库 → Top候选化合物列表
    """

    def __init__(
        self,
        docking_engine: Optional[DockingEngine] = None,
        hit_threshold: float = 6.0,
        output_dir: str = "./screening_results"
    ):
        self.library = CompoundLibrary()
        self.docking = docking_engine or DockingEngine(output_dir=output_dir)
        self.scorer = AffinityScorer(hit_threshold=hit_threshold)

    def screen(
        self,
        target_chembl_id: str,
        protein_pdb: Optional[str] = None,
        library_source: str = "chembl",
        max_compounds: int = 500,
        top_n: int = 20,
        use_docking: bool = False
    ) -> ScreeningResult:
        """
        执行虚拟筛选

        Args:
            target_chembl_id: ChEMBL靶点ID
            protein_pdb: 蛋白质PDB文件路径（对接用）
            library_source: 化合物库来源 (chembl/pubchem)
            max_compounds: 最大筛选数
            top_n: 返回Top N结果
            use_docking: 是否执行分子对接
        """
        logger.info(f"=== 开始虚拟筛选: {target_chembl_id} ===")

        # Step 1: 获取化合物库
        logger.info("Step 1: 获取化合物库...")
        if library_source == "chembl":
            compounds = self.library.fetch_target_compounds(
                target_chembl_id, limit=max_compounds
            )
        else:
            # 可扩展其他来源
            compounds = self.library.fetch_target_compounds(
                target_chembl_id, limit=max_compounds
            )

        if not compounds:
            return ScreeningResult(
                target=target_chembl_id,
                total_screened=0,
                hits_found=0,
                top_candidates=[],
                method="none",
                summary="未找到相关化合物数据"
            )

        # Step 2: Lipinski过滤
        logger.info("Step 2: Lipinski规则过滤...")
        filtered = self.library.apply_lipinski_filter(compounds)
        filtered = self.library.deduplicate(filtered)
        logger.info(f"Lipinski过滤后: {len(filtered)} 个化合物")

        # Step 3: 亲和力评分
        logger.info("Step 3: 亲和力评分...")
        compound_dicts = [asdict(c) for c in filtered]
        scored = self.scorer.score_by_descriptors(compound_dicts)

        # Step 4: 可选对接
        docking_results = []
        if use_docking and protein_pdb:
            logger.info("Step 4: 分子对接...")
            top_smiles = [s.smiles for s in scored[:50]]
            if self.docking.diffdock_path:
                docking_results = self.docking.dock_diffdock(protein_pdb, top_smiles)
            elif self.docking.vina_path:
                docking_results = self.docking.dock_vina(protein_pdb, top_smiles)

        # 合并结果
        candidates = self._merge_results(scored, docking_results, filtered)

        # Top N
        hits = [c for c in candidates if c.get("is_hit", False)]
        top = candidates[:top_n]

        return ScreeningResult(
            target=target_chembl_id,
            total_screened=len(filtered),
            hits_found=len(hits),
            top_candidates=top,
            method="docking+scoring" if use_docking else "scoring",
            summary=f"筛选{len(filtered)}个化合物，找到{len(hits)}个hit，Top推荐{top_n}个候选"
        )

    def _merge_results(
        self,
        scored: list,
        docking_results: list,
        compounds: list[Compound]
    ) -> list[dict]:
        """合并评分和对接结果"""
        compound_map = {c.smiles: c for c in compounds}
        merged = []

        for s in scored:
            entry = {
                "smiles": s.smiles,
                "predicted_pkd": s.predicted_pkd,
                "confidence": s.confidence,
                "percentile_rank": s.percentile_rank,
                "is_hit": s.is_hit,
            }

            # 合并化合物属性
            comp = compound_map.get(s.smiles)
            if comp:
                entry["name"] = comp.name
                entry["chembl_id"] = comp.chembl_id
                entry["mw"] = comp.mw
                entry["logp"] = comp.logp

            # 合并对接结果
            for dr in docking_results:
                if dr.smiles == s.smiles:
                    entry["docking_score"] = dr.binding_score
                    entry["docking_confidence"] = dr.confidence
                    break

            merged.append(entry)

        return merged
