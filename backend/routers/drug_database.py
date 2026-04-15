"""Drug Database API"""
from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter(prefix="/drugs", tags=["Drug Database"])
from backend.biomedical.drug_database.engine import drug_db

@router.get("/search")
async def search(q: str):
    return drug_db.search(q)

@router.get("/{drug_id}")
async def get_drug(drug_id: str):
    r = drug_db.get(drug_id)
    if not r: raise HTTPException(404, f"Not found: {drug_id}")
    return r

@router.get("/")
async def list_all(category: Optional[str] = None):
    return drug_db.list_all(category)

@router.get("/target/{target}")
async def by_target(target: str):
    return drug_db.by_target(target)
