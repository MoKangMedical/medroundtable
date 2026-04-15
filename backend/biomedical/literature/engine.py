"""Literature Intelligence Engine — PubMed/ArXiv search and analysis"""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class LiteratureEngine:
    """Search and analyze biomedical literature."""

    SAMPLE_PAPERS = [
        {"pmid":"PMID:38012345","title":"AlphaFold3 predicts protein-ligand interactions with unprecedented accuracy",
         "journal":"Nature","year":2025,"citations":342,"keywords":["protein structure","drug discovery","AI"],
         "abstract":"We present AlphaFold3, which extends protein structure prediction to protein-ligand complexes..."},
        {"pmid":"PMID:38123456","title":"GLP-1受体激动剂在心血管保护中的新证据",
         "journal":"NEJM","year":2025,"citations":189,"keywords":["GLP-1","cardiovascular","obesity"],
         "abstract":"This randomized trial demonstrates significant cardiovascular benefits of semaglutide..."},
        {"pmid":"PMID:38234567","title":"Single-cell multi-omics reveals tumor heterogeneity",
         "journal":"Cell","year":2025,"citations":276,"keywords":["single cell","cancer","multi-omics"],
         "abstract":"We applied single-cell ATAC-seq and RNA-seq to 50 tumors across 8 cancer types..."},
        {"pmid":"PMID:38345678","title":"DiffDock achieves blind molecular docking at scale",
         "journal":"Nature Methods","year":2025,"citations":156,"keywords":["docking","diffusion","molecular modeling"],
         "abstract":"DiffDock uses diffusion generative models for blind molecular docking..."},
        {"pmid":"PMID:38456789","title":"CRISPR base editing corrects sickle cell disease in vivo",
         "journal":"Science","year":2025,"citations":234,"keywords":["CRISPR","gene editing","sickle cell"],
         "abstract":"We demonstrate efficient correction of the sickle cell mutation using adenine base editors..."},
        {"pmid":"PMID:38567890","title":"AI-driven drug repurposing for rare diseases: a systematic review",
         "journal":"Lancet Digital Health","year":2025,"citations":98,"keywords":["drug repurposing","rare disease","AI"],
         "abstract":"This systematic review evaluates AI methods for identifying repurposing opportunities..."},
    ]

    def search(self, query: str, limit: int = 10, year_from: Optional[int] = None) -> List[Dict]:
        results = []
        for p in self.SAMPLE_PAPERS:
            if (query.lower() in p["title"].lower() or
                query.lower() in " ".join(p["keywords"]).lower() or
                query.lower() in p.get("abstract","").lower()):
                if year_from and p["year"] < year_from: continue
                results.append(p)
        return results[:limit]

    def get_paper(self, pmid: str) -> Optional[Dict]:
        for p in self.SAMPLE_PAPERS:
            if p["pmid"] == pmid: return p
        return None

    def trending(self, limit: int = 5) -> List[Dict]:
        return sorted(self.SAMPLE_PAPERS, key=lambda x: x["citations"], reverse=True)[:limit]

    def analyze_topic(self, topic: str) -> Dict[str, Any]:
        papers = self.search(topic, limit=20)
        total_citations = sum(p["citations"] for p in papers)
        all_keywords = []
        for p in papers: all_keywords.extend(p["keywords"])
        from collections import Counter
        top_kw = Counter(all_keywords).most_common(5)
        return {"topic":topic,"paper_count":len(papers),"total_citations":total_citations,
                "top_keywords":top_kw,"avg_citations":total_citations/max(len(papers),1)}


lit_engine = LiteratureEngine()
