"""
Gene Panel Analysis for Rare Disease Screening
"""
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class GenePanelAnalyzer:
    """Analyze gene panels for rare disease screening."""

    GENE_PANELS = {
        "neurological": ["SMN1", "SMN2", "DMD", "HTT", "FMR1", "ATM", "ATP7B", "GLA", "PLP1", "MECP2"],
        "metabolic": ["PAH", "GALT", "HEXA", "GALT", "GBA", "GLA", "SLC22A5", "ACADM", "HMGCL"],
        "cardiac": ["MYH7", "MYBPC3", "TNNT2", "SCN5A", "KCNQ1", "KCNH2", "RYR2", "DSP", "PKP2"],
        "immunological": ["BTK", "IL2RG", "RAG1", "RAG2", "JAK3", "WASP", "FOXP3", "AIRE", "CD40LG"],
        "hematological": ["F8", "F9", "HBB", "HBA1", "HBA2", "GATA1", "ANK1", "SLC4A1", "EPB42"],
    }

    def __init__(self):
        pass

    def get_panel(self, panel_type: str) -> Dict[str, Any]:
        """Get gene panel by type."""
        genes = self.GENE_PANELS.get(panel_type, [])
        return {
            "panel_type": panel_type,
            "genes": genes,
            "gene_count": len(genes),
            "description": f"{panel_type} rare disease screening panel"
        }

    def list_panels(self) -> List[Dict[str, Any]]:
        """List all available gene panels."""
        return [{"type": k, "gene_count": len(v), "description": f"{k} screening panel"} for k, v in self.GENE_PANELS.items()]

    def analyze_variants(self, gene: str, variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze variants in a gene for disease association."""
        # Simplified analysis
        pathogenic_count = sum(1 for v in variants if v.get("classification") in ["pathogenic", "likely_pathogenic"])
        return {
            "gene": gene,
            "total_variants": len(variants),
            "pathogenic_count": pathogenic_count,
            "clinical_significance": "significant" if pathogenic_count > 0 else "uncertain",
            "recommendation": "Genetic counseling recommended" if pathogenic_count > 0 else "Monitor and reclassify as needed"
        }


gene_panel_analyzer = GenePanelAnalyzer()
