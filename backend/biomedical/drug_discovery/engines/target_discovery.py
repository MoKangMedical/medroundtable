"""
靶点发现主引擎
整合PubMed挖掘、知识图谱查询、靶点评分，输出靶点评估报告
"""

import logging
from dataclasses import dataclass, asdict
from typing import Optional

from openai import OpenAI

from .pubmed_miner import PubMedMiner
from .knowledge_graph import KnowledgeGraphQuery
from .scorer import TargetScorer

logger = logging.getLogger(__name__)


@dataclass
class TargetReport:
    """靶点评估报告"""
    disease: str
    total_candidates: int
    top_targets: list[dict]
    methodology: str
    summary: str


class TargetDiscoveryEngine:
    """
    靶点发现引擎
    疾病名称 → 候选靶点排名报告
    """

    def __init__(
        self,
        llm_client: Optional[OpenAI] = None,
        llm_model: str = "mimo-v2-pro",
        email: str = "medipharma@example.com"
    ):
        self.miner = PubMedMiner(email=email)
        self.kg = KnowledgeGraphQuery()
        self.scorer = TargetScorer()
        self.llm = llm_client
        self.model = llm_model

    def discover_targets(
        self,
        disease: str,
        max_papers: int = 50,
        top_n: int = 10,
        disease_burden: float = 0.8,
        unmet_need: float = 0.8
    ) -> TargetReport:
        """
        完整靶点发现流水线

        Args:
            disease: 目标疾病名称
            max_papers: 最大检索文献数
            top_n: 返回Top N靶点
            disease_burden: 疾病负担评分 (0-1)
            unmet_need: 未满足需求评分 (0-1)

        Returns:
            TargetReport: 靶点评估报告
        """
        logger.info(f"=== 开始靶点发现: {disease} ===")

        # Step 1: PubMed文献挖掘
        logger.info("Step 1: PubMed文献挖掘...")
        evidence_list = self.miner.full_mining_pipeline(
            disease=disease,
            max_papers=max_papers,
            llm_client=self.llm
        )

        # Step 2: 知识图谱查询
        logger.info("Step 2: 知识图谱靶点画像...")
        gene_symbols = [e["gene_symbol"] for e in evidence_list[:20]]
        target_profiles = self.kg.batch_target_profile(gene_symbols)

        # 合并数据
        merged = self._merge_evidence_profiles(evidence_list, target_profiles)

        # 注入疾病参数
        for m in merged:
            m["disease_burden"] = disease_burden
            m["unmet_need"] = unmet_need

        # Step 3: 靶点评分排序
        logger.info("Step 3: 靶点多维评分...")
        ranked = self.scorer.rank_targets(merged)
        top_targets = [asdict(r) for r in ranked[:top_n]]

        # Step 4: 生成报告摘要
        summary = self._generate_summary(disease, top_targets)

        return TargetReport(
            disease=disease,
            total_candidates=len(ranked),
            top_targets=top_targets,
            methodology="PubMed文献挖掘 + 多源知识图谱 + 多维评分",
            summary=summary
        )

    def _merge_evidence_profiles(
        self,
        evidence: list[dict],
        profiles: list[dict]
    ) -> list[dict]:
        """合并文献证据和知识图谱画像"""
        profile_map = {p["gene_symbol"]: p for p in profiles if "gene_symbol" in p}
        merged = []

        for e in evidence:
            gene = e["gene_symbol"]
            profile = profile_map.get(gene, {})

            merged.append({
                "gene_symbol": gene,
                "evidence_strength": e.get("evidence_strength", "weak"),
                "total_papers": e.get("total_papers", 0),
                "known_drugs": profile.get("known_drugs", 0),
                "has_3d_structure": bool(profile.get("uniprot_id")),
                "is_essential_gene": False,  # 可后续增强
                "disease_associations": profile.get("diseases", e.get("disease_associations", [])),
                "protein_name": profile.get("protein_name", ""),
                "druggability_score": profile.get("druggability_score", 0.5),
                "novelty_score": profile.get("novelty_score", 0.5),
            })

        return merged

    def _generate_summary(self, disease: str, top_targets: list[dict]) -> str:
        """生成靶点发现报告摘要"""
        if not top_targets:
            return f"未找到与{disease}相关的候选靶点。"

        if self.llm:
            try:
                targets_text = "\n".join([
                    f"- {t['gene_symbol']}: 综合分{t['total_score']}, "
                    f"证据{t['evidence_score']}, 可药性{t['druggability_score']}, "
                    f"新颖性{t['novelty_score']}, 推荐{t['recommendation']}"
                    for t in top_targets[:5]
                ])
                resp = self.llm.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是药物研发专家。根据以下靶点评分结果，撰写一份简洁的靶点发现报告摘要（200字以内），重点说明Top靶点的开发价值和建议。"
                        },
                        {
                            "role": "user",
                            "content": f"疾病：{disease}\n\nTop候选靶点：\n{targets_text}"
                        }
                    ],
                    temperature=0.3
                )
                return resp.choices[0].message.content
            except Exception as e:
                logger.warning(f"LLM摘要生成失败: {e}")

        # fallback摘要
        top_gene = top_targets[0]["gene_symbol"]
        strong_count = sum(1 for t in top_targets if t["recommendation"] == "strong")
        return (f"针对{disease}，共分析{len(top_targets)}个候选靶点。"
                f"Top推荐靶点为{top_gene}，综合评分{top_targets[0]['total_score']}。"
                f"其中{strong_count}个靶点获得strong推荐。")
