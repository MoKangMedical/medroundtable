"""Rare Disease API — MediChat-RD capabilities"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/rare-disease", tags=["Rare Disease"])
from backend.biomedical.rare_disease.engine import rare_engine

class SymptomReq(BaseModel):
    symptoms: List[str]
    top_k: int = 5

@router.post("/diagnose")
async def diagnose(req: SymptomReq):
    return rare_engine.differential(req.symptoms)

@router.get("/disease/{did}")
async def get_disease(did: str):
    r = rare_engine.get_disease(did)
    if not r: raise HTTPException(404, f"Not found: {did}")
    return r

@router.get("/diseases")
async def list_diseases(category: Optional[str] = None):
    return rare_engine.list_diseases(category)
