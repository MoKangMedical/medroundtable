"""Verify signed research plans before a Windows connector executes a job."""
import hashlib
import hmac
import json
from typing import Any, Dict, Set


def canonical_plan(plan: Dict[str, Any]) -> bytes:
    return json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def verify_plan_signature(plan: Dict[str, Any], expected_hash: str, signature: str, secret: str) -> bool:
    body = canonical_plan(plan)
    actual_hash = hashlib.sha256(body).hexdigest()
    expected_signature = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(actual_hash, expected_hash) and hmac.compare_digest(expected_signature, signature)


def assert_executable(job: Dict[str, Any], secret: str, allowed_paths: Set[str]) -> None:
    path = job.get("analysis_path")
    plan = job.get("research_plan")
    if path not in allowed_paths:
        raise ValueError(f"analysis path is not allowed: {path}")
    if not isinstance(plan, dict) or not verify_plan_signature(
        plan, job.get("plan_hash", ""), job.get("plan_signature", ""), secret
    ):
        raise ValueError("research plan signature verification failed")
