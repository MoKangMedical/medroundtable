# Production local-job integration

## 1. Persistent store on Tencent Cloud

Set the backend service environment:

```bash
MRT_JOB_DB=/var/lib/medroundtable/local_jobs.sqlite3
MRT_JOB_SIGNING_SECRET=<long-random-server-secret>
```

Create the directory with write permission for the backend user. For multiple backend workers, migrate this store to PostgreSQL before enabling concurrent job writers.

## 2. Relay queue adapter

The web backend must enqueue the signed job into the authenticated relay queue, not only return it from the HTTP request. Configure the relay base URL and token in the backend service, then map these operations:

```text
web POST /api/v1/local-jobs/from-research-plan
  -> relay POST /api/v1/relay/jobs
connector GET /api/v1/relay/jobs/poll
connector POST /api/v1/relay/jobs/{job_id}/result
connector POST /api/v1/relay/jobs/{job_id}/failed
```

Do not accept arbitrary `analysis_path`; validate against the connector allowlist before enqueueing.

## 3. Connector verification gate

Before executing a polled job, Windows must call `bridge.plan_verifier.assert_executable(job, MRT_JOB_SIGNING_SECRET, ALLOWED_PATHS)`. On any failure it must POST `/failed`, write an audit event, and never call the local API.

## 4. Result and paper return

The result callback may include only aggregate tables, chart/report paths, `audit_id`, and an optional `paper_draft`. It must reject `raw_data`, `raw_rows`, `file_content`, and Ollama prompt/context fields.
