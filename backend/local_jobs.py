"""MVP local-analysis job contract for the MedRoundTable web UI.

Production deployment should back this contract with the authenticated relay
queue; this in-process store is intentionally only a local integration stub.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/local-jobs", tags=["local-jobs"])
_jobs: Dict[str, Dict[str, Any]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CreateLocalJobRequest(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    dataset_id: str = Field(min_length=1, max_length=120)
    analysis_path: str = Field(min_length=1, max_length=120)
    payload: Dict[str, Any] = Field(default_factory=dict)
    requested_by: str = Field(default="web-user", max_length=120)


class JobResultRequest(BaseModel):
    result: Dict[str, Any] = Field(default_factory=dict)
    audit_id: Optional[str] = None


class JobFailureRequest(BaseModel):
    error: str = Field(min_length=1, max_length=2000)


@router.post("", status_code=202)
async def create_local_job(request: CreateLocalJobRequest):
    job_id = str(uuid4())
    job = {
        "job_id": job_id,
        "title": request.title,
        "dataset_id": request.dataset_id,
        "analysis_path": request.analysis_path,
        "payload": request.payload,
        "requested_by": request.requested_by,
        "status": "queued",
        "created_at": _now().isoformat(),
        "updated_at": _now().isoformat(),
        "result": None,
        "audit_id": None,
        "error": None,
    }
    _jobs[job_id] = job
    return job


@router.get("")
async def list_local_jobs(limit: int = 20) -> List[Dict[str, Any]]:
    return list(reversed(list(_jobs.values())))[: max(1, min(limit, 100))]


@router.get("/{job_id}")
async def get_local_job(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="local job not found")
    return job


@router.post("/{job_id}/result")
async def complete_local_job(job_id: str, request: JobResultRequest):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="local job not found")
    job.update(status="completed", result=request.result, audit_id=request.audit_id, updated_at=_now().isoformat())
    return job


@router.post("/{job_id}/failed")
async def fail_local_job(job_id: str, request: JobFailureRequest):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="local job not found")
    job.update(status="failed", error=request.error, updated_at=_now().isoformat())
    return job
