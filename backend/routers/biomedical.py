"""
Biomedical Research API Router — MedRoundTable
Unified API for drug discovery, single-cell, checkpoints, MCP tools, molecular viz
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

router = APIRouter(prefix="/biomedical", tags=["Biomedical Research Hub"])


# ===== Request/Response Models =====

class DrugDiscoveryRequest(BaseModel):
    disease: str = Field(..., description="Target disease name")
    pipeline_stages: List[str] = Field(
        default=["target_discovery", "virtual_screening", "molecular_generation", "admet_prediction"],
        description="Pipeline stages to execute"
    )
    max_candidates: int = Field(default=10, description="Max candidate molecules")
    dry_run: bool = Field(default=False, description="Preview without execution")


class CheckpointCreateRequest(BaseModel):
    operation_type: str = Field(..., description="Type of operation (diagnosis, drug_discovery, analysis)")
    risk_level: str = Field(default="medium", description="low/medium/high/critical")
    description: str = Field("", description="Operation description")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CheckpointActionRequest(BaseModel):
    checkpoint_id: str
    reason: str = Field("", description="Reason for confirm/reject")


class MCPToolCallRequest(BaseModel):
    args: Dict[str, Any] = Field(default_factory=dict)


class PDBVizRequest(BaseModel):
    pdb_text: str = Field(..., description="PDB file content")
    radius_scale: float = Field(default=0.5, description="Atom radius scale factor")
    opacity: float = Field(default=0.9, description="Splat opacity")


# ===== Endpoints =====

@router.get("/health")
async def biomedical_health():
    """Biomedical hub health check."""
    return {"status": "ok", "modules": ["drug_discovery", "single_cell", "checkpoints", "mcp_tools", "mol_viz"]}


# --- Drug Discovery ---

@router.post("/drug-discovery/run")
async def run_drug_discovery(req: DrugDiscoveryRequest):
    """Run drug discovery pipeline."""
    try:
        from backend.biomedical.drug_discovery.pipeline import PipelineConfig
        return {
            "status": "accepted",
            "disease": req.disease,
            "stages": req.pipeline_stages,
            "max_candidates": req.max_candidates,
            "dry_run": req.dry_run,
            "message": "Drug discovery pipeline queued" if not req.dry_run else "Dry run — no execution",
        }
    except ImportError:
        raise HTTPException(status_code=503, detail="Drug discovery module not fully loaded. Check dependencies.")


@router.get("/drug-discovery/status/{pipeline_id}")
async def drug_discovery_status(pipeline_id: str):
    """Get pipeline status."""
    return {"pipeline_id": pipeline_id, "status": "not_found", "message": "Pipeline tracking not yet initialized"}


# --- Single-Cell ---

@router.get("/single-cell/models")
async def list_single_cell_models(task: Optional[str] = None):
    """List available single-cell models."""
    from backend.biomedical.single_cell.hub import hub
    return {"models": hub.list_models(task=task), "total": len(hub.models)}


@router.get("/single-cell/datasets")
async def list_single_cell_datasets(organism: Optional[str] = None):
    """List available single-cell datasets."""
    from backend.biomedical.single_cell.hub import hub
    return {"datasets": hub.list_datasets(organism=organism), "total": len(hub.datasets)}


@router.get("/single-cell/tasks")
async def list_single_cell_tasks():
    """List single-cell task types."""
    from backend.biomedical.single_cell.hub import hub
    return {"tasks": hub.list_tasks()}


@router.get("/single-cell/models/{model_id}")
async def get_single_cell_model(model_id: str):
    """Get model details."""
    from backend.biomedical.single_cell.hub import hub
    model = hub.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    return model


# --- Decision Checkpoints ---

_checkpoint_store: Dict[str, Dict[str, Any]] = {}
_checkpoint_counter = 0


@router.post("/checkpoints/create")
async def create_checkpoint(req: CheckpointCreateRequest):
    """Create a decision checkpoint for human review."""
    global _checkpoint_counter
    _checkpoint_counter += 1
    cid = f"cp_{_checkpoint_counter:06d}"
    _checkpoint_store[cid] = {
        "id": cid,
        "operation_type": req.operation_type,
        "risk_level": req.risk_level,
        "description": req.description,
        "metadata": req.metadata,
        "status": "pending",
    }
    return {"checkpoint_id": cid, "status": "pending", "message": "Checkpoint created — awaiting human review"}


@router.get("/checkpoints/{checkpoint_id}")
async def get_checkpoint(checkpoint_id: str):
    """Get checkpoint status."""
    cp = _checkpoint_store.get(checkpoint_id)
    if not cp:
        raise HTTPException(status_code=404, detail=f"Checkpoint '{checkpoint_id}' not found")
    return cp


@router.post("/checkpoints/{checkpoint_id}/confirm")
async def confirm_checkpoint(checkpoint_id: str, req: CheckpointActionRequest):
    """Confirm a checkpoint (approve operation)."""
    cp = _checkpoint_store.get(checkpoint_id)
    if not cp:
        raise HTTPException(status_code=404, detail=f"Checkpoint '{checkpoint_id}' not found")
    cp["status"] = "confirmed"
    cp["action_reason"] = req.reason
    return {"checkpoint_id": checkpoint_id, "status": "confirmed", "message": "Operation approved"}


@router.post("/checkpoints/{checkpoint_id}/reject")
async def reject_checkpoint(checkpoint_id: str, req: CheckpointActionRequest):
    """Reject a checkpoint (abort operation)."""
    cp = _checkpoint_store.get(checkpoint_id)
    if not cp:
        raise HTTPException(status_code=404, detail=f"Checkpoint '{checkpoint_id}' not found")
    cp["status"] = "rejected"
    cp["action_reason"] = req.reason
    return {"checkpoint_id": checkpoint_id, "status": "rejected", "message": "Operation aborted"}


# --- MCP Tools ---

@router.get("/mcp-tools")
async def list_mcp_tools(category: Optional[str] = None):
    """List available MCP biomedical tools."""
    from backend.biomedical.mcp_tools import registry
    return {
        "tools": registry.list_tools(category=category),
        "categories": registry.list_categories(),
        "total": len(registry._tools),
    }


@router.post("/mcp-tools/{tool_name}/call")
async def call_mcp_tool(tool_name: str, req: MCPToolCallRequest):
    """Call an MCP tool."""
    from backend.biomedical.mcp_tools import registry
    result = await registry.call_tool(tool_name, req.args)
    if "error" in result and "not found" in result.get("error", ""):
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# --- Molecular Visualization ---

@router.post("/mol-viz/pdb")
async def pdb_to_splats(req: PDBVizRequest):
    """Convert PDB text to 3D splat visualization data."""
    from backend.biomedical.mol_viz import mol_viz
    atoms = mol_viz.parse_pdb_atoms(req.pdb_text)
    if not atoms:
        raise HTTPException(status_code=400, detail="No atoms found in PDB text")
    viz_data = mol_viz.molecular_to_viz({"atoms": atoms, "bonds": []})
    viz_data["splat_data"] = mol_viz.atoms_to_splats(atoms, req.radius_scale, req.opacity).to_dict()
    return viz_data


# ===== Top Open-Source Integration Endpoints =====

@router.get("/integrations/status")
async def integrations_status():
    """Check availability of external integrations."""
    try:
        from backend.biomedical.integrations import deepchem_bridge, pubchem_bridge, biotite_bridge
        return {
            "deepchem": deepchem_bridge.available,
            "pubchem": pubchem_bridge.available,
            "biotite": biotite_bridge.available,
            "rdkit": True,
        }
    except ImportError as e:
        return {"error": str(e), "deepchem": False, "pubchem": False, "biotite": False}


class CompoundLookupRequest(BaseModel):
    identifier: str
    identifier_type: str = "name"


@router.post("/compound/lookup")
async def compound_lookup(req: CompoundLookupRequest):
    """Look up compound from PubChem."""
    from backend.biomedical.integrations import pubchem_bridge
    if not pubchem_bridge.available:
        raise HTTPException(status_code=503, detail="PubChem bridge not available")
    result = pubchem_bridge.get_compound(req.identifier, req.identifier_type)
    if not result:
        raise HTTPException(status_code=404, detail=f"Compound not found: {req.identifier}")
    return result


class SimilaritySearchRequest(BaseModel):
    smiles: str
    top_k: int = 10


@router.post("/compound/similarity")
async def compound_similarity(req: SimilaritySearchRequest):
    """Find similar compounds via PubChem."""
    from backend.biomedical.integrations import pubchem_bridge
    if not pubchem_bridge.available:
        raise HTTPException(status_code=503, detail="PubChem bridge not available")
    results = pubchem_bridge.search_similar(req.smiles, max_results=req.top_k)
    return {"query_smiles": req.smiles, "results": results, "count": len(results)}


@router.post("/structure/parse")
async def parse_structure(req: PDBVizRequest):
    """Parse PDB structure using Biotite."""
    from backend.biomedical.integrations import biotite_bridge
    if not biotite_bridge.available:
        raise HTTPException(status_code=503, detail="Biotite bridge not available")
    structure = biotite_bridge.parse_pdb(req.pdb_text)
    sequences = biotite_bridge.extract_sequence(req.pdb_text)
    return {"structure": structure, "sequences": sequences}
