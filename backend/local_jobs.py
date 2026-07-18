"""Public website adapter for signed jobs in the authenticated relay queue."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import hmac
import json
import os
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.relay_router import ALLOWED_PATHS, _db, _job_response, init_relay_db

router = APIRouter(prefix="/api/v1/local-jobs", tags=["local-jobs"])
init_relay_db()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(plan: Dict[str, Any]) -> bytes:
    return json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _signed_plan(plan: Dict[str, Any]) -> Dict[str, str]:
    body = _canonical(plan)
    secret = os.getenv("MRT_JOB_SIGNING_SECRET") or os.getenv("MRT_CONNECTOR_TOKEN") or "development-only-change-me"
    return {
        "plan_hash": hashlib.sha256(body).hexdigest(),
        "plan_signature": hmac.new(secret.encode(), body, hashlib.sha256).hexdigest(),
    }


class CreateLocalJobRequest(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    dataset_id: str = Field(min_length=1, max_length=120)
    analysis_path: str = Field(min_length=1, max_length=120)
    payload: Dict[str, Any] = Field(default_factory=dict)
    requested_by: str = Field(default="web-user", max_length=120)
    node_id: str = Field(default="windows-medroundtable-local", max_length=64)


class DispatchResearchPlanRequest(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    dataset_id: str = Field(min_length=1, max_length=120)
    analysis_path: str = Field(min_length=1, max_length=120)
    research_plan: Dict[str, Any] = Field(min_length=1)
    requested_by: str = Field(default="roundtable-web", max_length=120)
    node_id: str = Field(default="windows-medroundtable-local", max_length=64)


class PublicResultRequest(BaseModel):
    result: Dict[str, Any] = Field(default_factory=dict)
    audit_id: Optional[str] = None
    paper_draft: Optional[str] = None


def _enqueue(title: str, dataset_id: str, analysis_path: str, payload: Dict[str, Any], plan: Dict[str, Any], requested_by: str, node_id: str):
    if analysis_path not in ALLOWED_PATHS:
        raise HTTPException(400, f"analysis_path not allowed: {analysis_path}")
    signed, job_id, now = _signed_plan(plan), str(uuid.uuid4()), _now()
    envelope = dict(payload)
    envelope.update({"research_plan": plan, "output_schema": "medroundtable.analysis-result/1.1"})
    with _db() as conn:
        conn.execute(
            "INSERT INTO local_jobs (job_id,title,dataset_id,analysis_path,payload,research_plan,plan_hash,plan_signature,requested_by,node_id,status,created_at,updated_at,schema_version) VALUES (?,?,?,?,?,?,?,?,?,?,'pending',?,?,?)",
            (job_id, title, dataset_id, analysis_path, json.dumps(envelope, ensure_ascii=False),
             json.dumps(plan, ensure_ascii=False), signed["plan_hash"], signed["plan_signature"],
             requested_by, node_id, now, now, "1.1"),
        )
        return _job_response(conn, job_id)


@router.post("", status_code=202)
async def create_local_job(request: CreateLocalJobRequest):
    plan = request.payload.get("research_plan") or request.payload
    return _enqueue(request.title, request.dataset_id, request.analysis_path, request.payload, plan, request.requested_by, request.node_id)


@router.post("/from-research-plan", status_code=202)
async def dispatch_research_plan(request: DispatchResearchPlanRequest):
    return _enqueue(request.title, request.dataset_id, request.analysis_path, {}, request.research_plan, request.requested_by, request.node_id)


@router.get("")
async def list_local_jobs(limit: int = 20) -> List[Dict[str, Any]]:
    with _db() as conn:
        ids = [row[0] for row in conn.execute("SELECT job_id FROM local_jobs ORDER BY created_at DESC LIMIT ?", (max(1, min(limit, 100)),))]
        return [_job_response(conn, job_id) for job_id in ids]


@router.get("/{job_id}")
async def get_local_job(job_id: str):
    with _db() as conn:
        return _job_response(conn, job_id)


@router.post("/{job_id}/result")
async def complete_local_job(job_id: str, request: PublicResultRequest):
    """Local-development callback; production connectors use the authenticated relay route."""
    now = _now()
    with _db() as conn:
        if not conn.execute("SELECT 1 FROM local_jobs WHERE job_id=?", (job_id,)).fetchone():
            raise HTTPException(404, "Job not found")
        conn.execute("UPDATE local_jobs SET status='completed',updated_at=? WHERE job_id=?", (now, job_id))
        conn.execute(
            "INSERT OR REPLACE INTO local_job_results (job_id,status,result,audit_id,posted_at,paper_draft,artifacts) VALUES (?,'completed',?,?,?,?,?)",
            (job_id, json.dumps(request.result, ensure_ascii=False), request.audit_id, now, request.paper_draft, "[]"),
        )
        return _job_response(conn, job_id)
