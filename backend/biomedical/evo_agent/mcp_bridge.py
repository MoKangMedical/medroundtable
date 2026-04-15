"""
EvoAgentX Bridge — MCP tools + Workflow wrapping for medroundtable
Wraps EvoAgentX's MCP, Agent, Workflow, Memory, Optimizer capabilities
"""
from typing import Any, Dict, List, Optional
import logging
import sys
import os

logger = logging.getLogger(__name__)

EVOAGENTX_PATH = "/root/EvoAgentX"
if EVOAGENTX_PATH not in sys.path:
    sys.path.insert(0, EVOAGENTX_PATH)

try:
    from evoagentx.tools.mcp import MCPToolkit, MCPTool
    from evoagentx.tools.tool import Toolkit, Tool
    from evoagentx.tools.search_base import SearchBase
    from evoagentx.tools.request_base import RequestBase
    EVO_TOOLS = True
except ImportError as e:
    logger.warning(f"EvoAgentX tools not available: {e}")
    EVO_TOOLS = False


class EvoMCPCatalog:
    """Catalog of EvoAgentX MCP-compatible tools for medroundtable."""

    TOOLS = {
        "pubmed": {"name": "PubMed Search", "desc": "Search biomedical literature", "category": "literature"},
        "chembl": {"name": "ChEMBL Query", "desc": "Drug target and compound data", "category": "drug_discovery"},
        "openfda": {"name": "OpenFDA", "desc": "FDA drug safety and labeling", "category": "drug_safety"},
        "omim": {"name": "OMIM", "desc": "Mendelian disease genetics", "category": "genetics"},
        "open_targets": {"name": "OpenTargets", "desc": "Target-disease associations", "category": "target_discovery"},
        "clinicaltrials": {"name": "ClinicalTrials.gov", "desc": "Clinical trial registry", "category": "clinical"},
        "uniprot": {"name": "UniProt", "desc": "Protein sequence and function", "category": "proteomics"},
        "pdb": {"name": "PDB", "desc": "Protein 3D structures", "category": "structural"},
        "reactome": {"name": "Reactome", "desc": "Biological pathways", "category": "pathways"},
        "go": {"name": "Gene Ontology", "desc": "Gene function annotation", "category": "functional_genomics"},
    }

    def list_all(self, category: Optional[str] = None) -> List[Dict]:
        return [{"id": k, **v} for k, v in self.TOOLS.items() if not category or v.get("category") == category]

    def get_categories(self) -> List[str]:
        return list(set(v.get("category", "") for v in self.TOOLS.values()))


class EvoWorkflowEngine:
    """Workflow execution engine wrapping EvoAgentX workflows."""

    WORKFLOW_TEMPLATES = {
        "drug_discovery_pipeline": {
            "name": "药物发现流水线",
            "steps": ["target_discovery", "virtual_screening", "molecular_generation", "admet_prediction", "lead_optimization"],
            "agents": ["drug_discoverer", "data_analyst"],
        },
        "literature_analysis": {
            "name": "文献分析流水线",
            "steps": ["search", "extract", "analyze", "summarize", "report"],
            "agents": ["literature_reviewer"],
        },
        "clinical_decision": {
            "name": "临床决策流水线",
            "steps": ["symptom_input", "differential_diagnosis", "treatment_plan", "drug_interaction_check"],
            "agents": ["clinical_advisor"],
        },
        "mdt_roundtable": {
            "name": "MDT圆桌讨论",
            "steps": ["case_presentation", "specialist_input", "debate", "consensus", "treatment_plan"],
            "agents": ["clinical_advisor", "drug_discoverer", "data_analyst", "literature_reviewer"],
        },
    }

    def list_workflows(self) -> List[Dict]:
        return [{"id": k, **v} for k, v in self.WORKFLOW_TEMPLATES.items()]

    def get_workflow(self, wf_id: str) -> Optional[Dict]:
        return self.WORKFLOW_TEMPLATES.get(wf_id)

    def create_workflow(self, wf_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        wf = self.WORKFLOW_TEMPLATES.get(wf_id)
        if not wf:
            return {"error": f"Unknown workflow: {wf_id}"}

        workflow_run_id = f"wf_{wf_id}_{hash(str(inputs)) % 10000:04d}"
        return {
            "workflow_id": workflow_run_id,
            "template": wf["name"],
            "steps": wf["steps"],
            "agents": wf["agents"],
            "inputs": inputs,
            "status": "queued",
            "evo_agentx_backend": EVO_TOOLS,
        }


evo_mcp_catalog = EvoMCPCatalog()
evo_workflow_engine = EvoWorkflowEngine()
