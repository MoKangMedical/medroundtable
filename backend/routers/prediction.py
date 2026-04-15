"""Prediction Engine API — Tianyan capabilities"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

router = APIRouter(prefix="/prediction", tags=["Prediction Engine"])
from backend.biomedical.prediction.engine import predictor

@router.get("/models")
async def list_models():
    return predictor.list_models()

class PredictReq(BaseModel):
    model_id: str
    features: Dict[str, Any]

@router.post("/predict")
async def predict(req: PredictReq):
    return predictor.predict(req.model_id, req.features)

class BatchPredictReq(BaseModel):
    model_id: str
    feature_list: List[Dict[str, Any]]

@router.post("/batch-predict")
async def batch_predict(req: BatchPredictReq):
    return predictor.batch_predict(req.model_id, req.feature_list)
