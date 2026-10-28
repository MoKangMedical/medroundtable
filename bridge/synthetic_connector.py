"""Poll one signed job and return a deterministic synthetic result."""
import argparse
import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request

from bridge.plan_verifier import assert_executable
from bridge.result_adapter import synthetic_paper, synthetic_result


def request_json(method: str, url: str, token: str, body=None):
    data = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
        return json.loads(raw.decode()) if raw else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--relay", default=os.getenv("MRT_PUBLIC_API", "https://medroundtable.cn/api/v1/relay"))
    parser.add_argument("--node-id", default=os.getenv("MRT_CONNECTOR_ID", "windows-medroundtable-local"))
    args = parser.parse_args()
    token = os.environ["MRT_CONNECTOR_TOKEN"]
    signing_secret = os.getenv("MRT_JOB_SIGNING_SECRET", token)
    relay = args.relay.rstrip("/")
    job = request_json("GET", relay + "/local-jobs/poll?" + urllib.parse.urlencode({"node_id": args.node_id}), token)
    if not job:
        print(json.dumps({"status": "idle", "message": "no pending job"}, ensure_ascii=False))
        return 0
    assert_executable(job, signing_secret, {"/api/analyze/quick", "/api/analyze/auto", "/api/analyze/hybrid"})
    result = synthetic_result(job["dataset_id"], job["job_id"])
    payload = {
        "status": "completed", "dataset_id": job["dataset_id"],
        "started_at": result["generated_at"], "finished_at": result["generated_at"],
        "result": result, "paper_draft": synthetic_paper(),
        "audit_id": "synthetic-" + job["job_id"],
        "artifacts": [{"type": "result_schema", "name": "analysis-result.json", "media_type": "application/json"}],
    }
    accepted = request_json("POST", f"{relay}/local-jobs/{job['job_id']}/result", token, payload)
    print(json.dumps({"status": "completed", "job_id": job["job_id"], "relay": accepted}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
