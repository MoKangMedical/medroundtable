"""MVP local-analysis job contract for the MedRoundTable web UI.

Production deployment should back this contract with the authenticated relay
queue; this in-process store is intentionally only a local integration stub.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4
import hashlib
import hmac
import json
import os
import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/local-jobs", tags=["local-jobs"])
_db_path = Path(os.getenv("MRT_JOB_DB", "medroundtable_jobs.sqlite3"))
_db_path.parent.mkdir(parents=True, exist_ok=True)
_conn = sqlite3.connect(_db_path, check_same_thread=False)
_conn.execute("CREATE TABLE IF NOT EXISTS local_jobs (job_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
_conn.commit()
_jobs: Dict[str, Dict[str, Any]] = {
    row[0]: json.loads(row[1]) for row in _conn.execute("SELECT job_id, payload FROM local_jobs")
}


def _save_job(job: Dict[str, Any]) -> None:
    _conn.execute(
        "INSERT OR REPLACE INTO local_jobs(job_id, payload) VALUES (?, ?)",
        (job["job_id"], json.dumps(job, ensure_ascii=False)),
    )
    _conn.commit()


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
    paper_draft: Optional[str] = None


class JobFailureRequest(BaseModel):
    error: str = Field(min_length=1, max_length=2000)


class DispatchResearchPlanRequest(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    dataset_id: str = Field(min_length=1, max_length=120)
    analysis_path: str = Field(min_length=1, max_length=120)
    research_plan: Dict[str, Any] = Field(min_length=1)
    requested_by: str = Field(default="roundtable-web", max_length=120)


def _signed_plan(plan: Dict[str, Any]) -> Dict[str, str]:
    canonical = json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    plan_hash = hashlib.sha256(canonical).hexdigest()
    secret = os.getenv("MRT_JOB_SIGNING_SECRET", "development-only-change-me").encode()
    signature = hmac.new(secret, canonical, hashlib.sha256).hexdigest()
    return {"plan_hash": plan_hash, "plan_signature": signature}


def _create_job(request: CreateLocalJobRequest, research_plan: Optional[Dict[str, Any]] = None):
    plan = research_plan or request.payload
    signed = _signed_plan(plan)
    now = _now().isoformat()
    job_id = str(uuid4())
    job = {
        "job_id": job_id,
        "title": request.title,
        "dataset_id": request.dataset_id,
        "analysis_path": request.analysis_path,
        "payload": request.payload,
        "research_plan": research_plan,
        **signed,
        "requested_by": request.requested_by,
        "status": "queued",
        "created_at": now,
        "updated_at": now,
        "result": None,
        "paper_draft": None,
        "audit_id": None,
        "error": None,
    }
    _jobs[job_id] = job
    _save_job(job)
    return job


@router.post("", status_code=202)
async def create_local_job(request: CreateLocalJobRequest):
    return _create_job(request)


@router.post("/from-research-plan", status_code=202)
async def dispatch_research_plan(request: DispatchResearchPlanRequest):
    """Convert an approved 14-agent plan into a signed local job envelope."""
    return _create_job(
        CreateLocalJobRequest(
            title=request.title,
            dataset_id=request.dataset_id,
            analysis_path=request.analysis_path,
            payload={"research_plan": request.research_plan},
            requested_by=request.requested_by,
        ),
        research_plan=request.research_plan,
    )


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
    job.update(status="completed", result=request.result, paper_draft=request.paper_draft, audit_id=request.audit_id, updated_at=_now().isoformat())
    _save_job(job)
    return job


@router.post("/{job_id}/failed")
async def fail_local_job(job_id: str, request: JobFailureRequest):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="local job not found")
    job.update(status="failed", error=request.error, updated_at=_now().isoformat())
    _save_job(job)
    return job
