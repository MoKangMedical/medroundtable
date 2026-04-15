"""Literature Intelligence API"""
from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter(prefix="/literature", tags=["Literature Intelligence"])
from backend.biomedical.literature.engine import lit_engine

@router.get("/search")
async def search(q: str, limit: int = 10, year_from: Optional[int] = None):
    return lit_engine.search(q, limit, year_from)

@router.get("/paper/{pmid}")
async def get_paper(pmid: str):
    r = lit_engine.get_paper(pmid)
    if not r: raise HTTPException(404, f"Not found: {pmid}")
    return r

@router.get("/trending")
async def trending(limit: int = 5):
    return lit_engine.trending(limit)

@router.get("/analyze/{topic}")
async def analyze_topic(topic: str):
    return lit_engine.analyze_topic(topic)
