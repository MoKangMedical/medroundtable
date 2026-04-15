"""Self-Evolving Agent API — EvoAgentX real integration"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

router = APIRouter(prefix="/evo", tags=["Evolving Agents"])

from backend.biomedical.evo_agent.engine import evo_engine
from backend.biomedical.evo_agent.mcp_bridge import evo_mcp_catalog, evo_workflow_engine


# ── Optimizers ──

@router.get("/optimizers")
async def list_optimizers():
    """List available evolutionary optimization methods."""
    return evo_engine.list_optimizers()


class EvolveReq(BaseModel):
    task: str
    method: str = "textgrad"
    iterations: int = 3

@router.post("/evolve")
async def evolve(req: EvolveReq):
    """Run workflow evolution optimization."""
    return evo_engine.evolve_workflow(req.task, req.method, req.iterations)


class EvolvePromptReq(BaseModel):
    task: str
    initial_prompt: str
    method: str = "evoprompt"
    iterations: int = 5

@router.post("/evolve-prompt")
async def evolve_prompt(req: EvolvePromptReq):
    """Evolve a prompt using evolutionary algorithms."""
    return evo_engine.evolve_prompt(req.task, req.initial_prompt, req.method, req.iterations)


# ── Agents ──

@router.get("/templates")
async def list_templates():
    """List available agent templates."""
    return evo_engine.list_agent_templates()


class CreateAgentReq(BaseModel):
    template_id: str
    goal: str
    model: str = "gpt-4o"

@router.post("/create")
async def create_agent(req: CreateAgentReq):
    """Create a specialized agent from template."""
    return evo_engine.create_agent(req.template_id, req.goal, req.model)


class DebateReq(BaseModel):
    topic: str
    agent_roles: List[str]
    rounds: int = 3

@router.post("/debate")
async def agents_debate(req: DebateReq):
    """Run multi-agent debate on a biomedical topic."""
    return evo_engine.run_agents_debate(req.topic, req.agent_roles, req.rounds)


@router.get("/agent/{agent_id}/status")
async def agent_status(agent_id: str):
    """Get status of a created agent."""
    return evo_engine.get_agent_status(agent_id)


class BenchmarkReq(BaseModel):
    task: str
    agents: List[str]
    eval_data: List[Dict[str, Any]]

@router.post("/benchmark")
async def benchmark_agents(req: BenchmarkReq):
    """Benchmark multiple agents on a task."""
    return evo_engine.benchmark_agents(req.task, req.agents, req.eval_data)


# ── MCP Tools ──

@router.get("/mcp-tools")
async def list_mcp_tools(category: Optional[str] = None):
    """List EvoAgentX MCP-compatible tools."""
    return evo_mcp_catalog.list_all(category)


@router.get("/mcp-tools/categories")
async def mcp_tool_categories():
    """List MCP tool categories."""
    return evo_mcp_catalog.get_categories()


# ── Workflows ──

@router.get("/workflows")
async def list_workflows():
    """List available workflow templates."""
    return evo_workflow_engine.list_workflows()


@router.get("/workflows/{wf_id}")
async def get_workflow(wf_id: str):
    """Get workflow template details."""
    r = evo_workflow_engine.get_workflow(wf_id)
    if not r: raise HTTPException(404, f"Workflow not found: {wf_id}")
    return r


class CreateWorkflowReq(BaseModel):
    workflow_id: str
    inputs: Dict[str, Any]

@router.post("/workflows/run")
async def run_workflow(req: CreateWorkflowReq):
    """Run a workflow with inputs."""
    return evo_workflow_engine.create_workflow(req.workflow_id, req.inputs)
