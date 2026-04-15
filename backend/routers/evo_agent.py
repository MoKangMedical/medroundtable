"""Self-Evolving Agent API — EvoAgentX integration"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, List

router = APIRouter(prefix="/evo", tags=["Evolving Agents"])
from backend.biomedical.evo_agent.engine import evo_engine

@router.get("/methods")
async def list_methods():
    return evo_engine.list_methods()

@router.get("/templates")
async def list_templates():
    return evo_engine.list_templates()

class EvolveReq(BaseModel):
    task: str
    method: str = "textgrad"
    iterations: int = 3

@router.post("/evolve")
async def evolve(req: EvolveReq):
    return evo_engine.evolve(req.task, req.method, req.iterations)

class CreateAgentReq(BaseModel):
    template_id: str
    goal: str

@router.post("/create")
async def create_agent(req: CreateAgentReq):
    return evo_engine.create_agent(req.template_id, req.goal)
