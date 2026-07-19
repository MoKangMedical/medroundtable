"""Authenticated Windows relay backed by the shared local-job SQLite queue."""
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import json
import os
import secrets
import sqlite3
import uuid

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["local-nodes"])
DB_PATH = os.getenv("MRT_RELAY_DB", "data/local_relay.db")
_TOKEN = os.getenv("MRT_CONNECTOR_TOKEN")
ALLOWED_PATHS = frozenset({
    "/api/inspect", "/api/search", "/api/explore/tables", "/api/explore/sql",
    "/api/analyze/quick", "/api/analyze/auto", "/api/analyze/hybrid", "/api/export",
})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _db():
    directory = os.path.dirname(DB_PATH) or "."
    os.makedirs(directory, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _add_columns(conn: sqlite3.Connection, table: str, columns: Dict[str, str]) -> None:
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    for name, ddl in columns.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")


def init_relay_db() -> None:
    with _db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS local_nodes (
                node_id TEXT PRIMARY KEY, hostname TEXT, local_api_version TEXT,
                registered_at TEXT, last_heartbeat TEXT
            );
            CREATE TABLE IF NOT EXISTS local_jobs (
                job_id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL, analysis_path TEXT NOT NULL,
                payload TEXT DEFAULT '{}', requested_by TEXT DEFAULT '', node_id TEXT DEFAULT '',
                status TEXT DEFAULT 'pending', created_at TEXT, dispatched_at TEXT
            );
            CREATE TABLE IF NOT EXISTS local_job_results (
                job_id TEXT PRIMARY KEY, status TEXT, dataset_id TEXT, started_at TEXT,
                finished_at TEXT, result TEXT, error TEXT, audit_id TEXT, posted_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_jobs_status ON local_jobs(status);
            CREATE INDEX IF NOT EXISTS idx_jobs_node ON local_jobs(node_id, status);
        """)
        _add_columns(conn, "local_jobs", {
            "title": "TEXT DEFAULT ''", "research_plan": "TEXT", "plan_hash": "TEXT",
            "plan_signature": "TEXT", "updated_at": "TEXT", "schema_version": "TEXT DEFAULT '1.1'",
        })
        _add_columns(conn, "local_job_results", {
            "paper_draft": "TEXT", "artifacts": "TEXT DEFAULT '[]'",
        })


init_relay_db()


def _verify_token(authorization: Optional[str]) -> None:
    if not _TOKEN:
        raise HTTPException(503, "Relay not configured: MRT_CONNECTOR_TOKEN not set")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing Bearer token")
    supplied = authorization.removeprefix("Bearer ").strip()
    if not secrets.compare_digest(supplied.encode(), _TOKEN.encode()):
        raise HTTPException(403, "Invalid connector token")


class NodeRegister(BaseModel):
    node_id: str = Field(min_length=1, max_length=64)
    hostname: str = ""
    local_api_version: str = ""


class JobCreate(BaseModel):
    dataset_id: str
    analysis_path: str
    payload: dict = Field(default_factory=dict)
    requested_by: str = ""
    node_id: str = ""
    status: str = "pending"


class JobResult(BaseModel):
    status: str = "completed"
    dataset_id: str = ""
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    audit_id: Optional[str] = None
    paper_draft: Optional[str] = None
    artifacts: list = Field(default_factory=list)


@router.get("/health")
@router.post("/health")
async def relay_health():
    return {"status": "ok", "service": "local-node-relay", "version": "3.0.0", "result_schema": "1.1"}


@router.post("/local-nodes/register")
async def register_node(body: NodeRegister, authorization: str = Header(...)):
    _verify_token(authorization)
    now = _now()
    with _db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO local_nodes VALUES (?, ?, ?, COALESCE((SELECT registered_at FROM local_nodes WHERE node_id=?), ?), ?)",
            (body.node_id, body.hostname, body.local_api_version, body.node_id, now, now),
        )
    return {"status": "registered", "node_id": body.node_id}


@router.post("/local-nodes/{node_id}/heartbeat")
async def heartbeat(node_id: str, authorization: str = Header(...)):
    _verify_token(authorization)
    with _db() as conn:
        conn.execute("UPDATE local_nodes SET last_heartbeat=? WHERE node_id=?", (_now(), node_id))
        row = conn.execute(
            "SELECT COUNT(*) FROM local_jobs WHERE status='pending' AND (node_id=? OR node_id='')", (node_id,)
        ).fetchone()
    return {"status": "alive", "pending_jobs": row[0]}


@router.post("/local-jobs")
async def create_job(body: JobCreate, authorization: str = Header(...)):
    _verify_token(authorization)
    if body.analysis_path not in ALLOWED_PATHS:
        raise HTTPException(400, f"analysis_path not allowed: {body.analysis_path}")
    job_id, now = str(uuid.uuid4()), _now()
    with _db() as conn:
        conn.execute(
            "INSERT INTO local_jobs (job_id,dataset_id,analysis_path,payload,requested_by,node_id,status,created_at,updated_at) VALUES (?,?,?,?,?,?,'pending',?,?)",
            (job_id, body.dataset_id, body.analysis_path, json.dumps(body.payload, ensure_ascii=False), body.requested_by, body.node_id, now, now),
        )
    return {"job_id": job_id, "status": "pending"}


@router.get("/local-jobs/poll")
async def poll_jobs(authorization: str = Header(...), node_id: Optional[str] = None):
    _verify_token(authorization)
    with _db() as conn:
        query = "SELECT * FROM local_jobs WHERE status='pending' "
        params = []
        if node_id:
            query += "AND (node_id=? OR node_id='') "
            params.append(node_id)
        query += "ORDER BY created_at LIMIT 1"
        row = conn.execute(query, params).fetchone()
        if not row:
            return None
        now = _now()
        conn.execute("UPDATE local_jobs SET status='dispatched',dispatched_at=?,updated_at=? WHERE job_id=?", (now, now, row["job_id"]))
        payload = json.loads(row["payload"] or "{}")
        plan = json.loads(row["research_plan"]) if row["research_plan"] else payload.get("research_plan")
        return {
            "schema_version": row["schema_version"] or "1.1", "job_id": row["job_id"],
            "title": row["title"], "dataset_id": row["dataset_id"], "dataset": row["dataset_id"],
            "analysis_path": row["analysis_path"],
            "payload": payload, "research_plan": plan, "plan_hash": row["plan_hash"],
            "plan_signature": row["plan_signature"], "requested_by": row["requested_by"],
            "result_contract": ["summary", "timeline", "agent_notes", "charts.forest", "charts.km", "charts.missingness", "tables.baseline", "tables.associations", "interpretation", "review_items", "paper_draft"],
        }


def _job_response(conn: sqlite3.Connection, job_id: str) -> Dict[str, Any]:
    job = conn.execute("SELECT * FROM local_jobs WHERE job_id=?", (job_id,)).fetchone()
    if not job:
        raise HTTPException(404, "Job not found")
    result = conn.execute("SELECT * FROM local_job_results WHERE job_id=?", (job_id,)).fetchone()
    return {
        "job_id": job["job_id"], "title": job["title"], "dataset_id": job["dataset_id"],
        "analysis_path": job["analysis_path"], "requested_by": job["requested_by"],
        "node_id": job["node_id"], "schema_version": job["schema_version"] or "1.1",
        "status": job["status"], "created_at": job["created_at"], "updated_at": job["updated_at"],
        "dispatched_at": job["dispatched_at"], "plan_hash": job["plan_hash"],
        "plan_signature": job["plan_signature"],
        "research_plan": json.loads(job["research_plan"]) if job["research_plan"] else None,
        "result": json.loads(result["result"]) if result and result["result"] else None,
        "error": result["error"] if result else None, "audit_id": result["audit_id"] if result else None,
        "paper_draft": result["paper_draft"] if result else None,
        "artifacts": json.loads(result["artifacts"] or "[]") if result else [],
    }


@router.get("/local-jobs/{job_id}")
async def get_job(job_id: str, authorization: str = Header(...)):
    _verify_token(authorization)
    with _db() as conn:
        return _job_response(conn, job_id)


@router.post("/local-jobs/{job_id}/result")
async def post_result(job_id: str, body: JobResult, authorization: str = Header(...)):
    _verify_token(authorization)
    now = _now()
    with _db() as conn:
        if not conn.execute("SELECT 1 FROM local_jobs WHERE job_id=?", (job_id,)).fetchone():
            raise HTTPException(404, "Job not found")
        conn.execute("UPDATE local_jobs SET status=?,updated_at=? WHERE job_id=?", (body.status, now, job_id))
        conn.execute(
            "INSERT OR REPLACE INTO local_job_results (job_id,status,dataset_id,started_at,finished_at,result,error,audit_id,posted_at,paper_draft,artifacts) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (job_id, body.status, body.dataset_id, body.started_at, body.finished_at,
             json.dumps(body.result, ensure_ascii=False) if body.result is not None else None,
             body.error, body.audit_id, now, body.paper_draft, json.dumps(body.artifacts, ensure_ascii=False)),
        )
    return {"status": "accepted", "job_id": job_id, "result_schema": "1.1"}


@router.post("/local-jobs/{job_id}/failed")
async def post_failure(job_id: str, body: JobResult, authorization: str = Header(...)):
    body.status = "failed"
    return await post_result(job_id, body, authorization)
