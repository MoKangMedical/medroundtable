"""Clinical Trials Search Engine — ClinicalTrials.gov integration"""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ClinicalTrialsEngine:
    """Search and analyze clinical trials."""

    SAMPLE_TRIALS = [
        {"nct_id":"NCT06123456","title":"GLP-1受体激动剂在NASH中的III期试验","phase":"Phase 3",
         "status":"Recruiting","condition":"NASH","intervention":"Semaglutide","sponsor":"Novo Nordisk",
         "enrollment":1200,"start_date":"2025-01","estimated_completion":"2027-06"},
        {"nct_id":"NCT06234567","title":"SMA基因治疗长期随访研究","phase":"Phase 4",
         "status":"Active, not recruiting","condition":"SMA","intervention":"Zolgensma","sponsor":"Novartis",
         "enrollment":300,"start_date":"2024-06","estimated_completion":"2029-12"},
        {"nct_id":"NCT06345678","title":"AI辅助罕见病诊断的前瞻性研究","phase":"Phase 2",
         "status":"Recruiting","condition":"Rare Diseases","intervention":"AI Diagnostic Tool","sponsor":"学术中心",
         "enrollment":500,"start_date":"2025-03","estimated_completion":"2026-12"},
        {"nct_id":"NCT06456789","title":"CAR-T细胞疗法治疗实体瘤","phase":"Phase 1/2",
         "status":"Recruiting","condition":"Solid Tumors","intervention":"CAR-T","sponsor":"学术中心",
         "enrollment":60,"start_date":"2025-06","estimated_completion":"2027-12"},
        {"nct_id":"NCT06567890","title":"减重药物联合GLP-1的疗效对比","phase":"Phase 3",
         "status":"Not yet recruiting","condition":"Obesity","intervention":"Tirzepatide","sponsor":"Eli Lilly",
         "enrollment":2000,"start_date":"2025-09","estimated_completion":"2028-06"},
    ]

    def search(self, query: str, status: Optional[str] = None, phase: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Search clinical trials by keyword."""
        results = []
        for t in self.SAMPLE_TRIALS:
            if query.lower() in t["title"].lower() or query.lower() in t["condition"].lower() or query.lower() in t["intervention"].lower():
                if status and t["status"] != status: continue
                if phase and t["phase"] != phase: continue
                results.append(t)
        return results[:limit]

    def get_trial(self, nct_id: str) -> Optional[Dict]:
        for t in self.SAMPLE_TRIALS:
            if t["nct_id"] == nct_id: return t
        return None

    def list_by_condition(self, condition: str) -> List[Dict]:
        return [t for t in self.SAMPLE_TRIALS if condition.lower() in t["condition"].lower()]

    def stats(self) -> Dict[str, Any]:
        by_status = {}
        by_phase = {}
        for t in self.SAMPLE_TRIALS:
            by_status[t["status"]] = by_status.get(t["status"], 0) + 1
            by_phase[t["phase"]] = by_phase.get(t["phase"], 0) + 1
        return {"total": len(self.SAMPLE_TRIALS), "by_status": by_status, "by_phase": by_phase}


trials_engine = ClinicalTrialsEngine()
