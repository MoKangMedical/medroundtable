"""Clinical Trials API"""
from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter(prefix="/trials", tags=["Clinical Trials"])
from backend.biomedical.clinical_trials.engine import trials_engine

@router.get("/search")
async def search(q: str, status: Optional[str] = None, phase: Optional[str] = None, limit: int = 10):
    return trials_engine.search(q, status, phase, limit)

@router.get("/{nct_id}")
async def get_trial(nct_id: str):
    r = trials_engine.get_trial(nct_id)
    if not r: raise HTTPException(404, f"Not found: {nct_id}")
    return r

@router.get("/condition/{condition}")
async def by_condition(condition: str):
    return trials_engine.list_by_condition(condition)

@router.get("/stats/overview")
async def stats():
    return trials_engine.stats()
