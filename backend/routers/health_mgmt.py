"""Health Management API — MediSlim capabilities"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

router = APIRouter(prefix="/health", tags=["Health Management"])
from backend.biomedical.health_mgmt.assessor import assessor, rx_checker

@router.get("/conditions")
async def list_conditions():
    return assessor.list_conditions()

@router.get("/questionnaire/{cid}")
async def get_questionnaire(cid: str):
    r = assessor.get_questionnaire(cid)
    if not r: raise HTTPException(404, f"Condition not found: {cid}")
    return r

class AssessReq(BaseModel):
    condition: str
    answers: Dict[str, Any]

@router.post("/assess")
async def assess(req: AssessReq):
    return assessor.assess(req.condition, req.answers)

class DrugCheckReq(BaseModel):
    drugs: List[str]

@router.post("/drug-check")
async def drug_check(req: DrugCheckReq):
    return rx_checker.check(req.drugs)

@router.get("/drug-check/{d1}/{d2}")
async def check_pair(d1: str, d2: str):
    from backend.biomedical.health_mgmt.assessor import INTERACTIONS
    k = (d1,d2) if (d1,d2) in INTERACTIONS else (d2,d1)
    if k in INTERACTIONS:
        return {"drug1":d1,"drug2":d2,"has_interaction":True,**INTERACTIONS[k]}
    return {"drug1":d1,"drug2":d2,"has_interaction":False}
