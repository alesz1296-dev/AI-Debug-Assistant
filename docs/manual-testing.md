# Manual Testing Checklist

Manual testing records runtime behavior that automated tests do not fully prove. Keep this file current when endpoint behavior, runtime dependencies, or validation commands change.

The GitHub Actions `compose-smoke` and `k8s-smoke` jobs mirror the current local platform checks in CI.

## Current Session

Date: 2026-06-20

Mode: API-only local run through `uvicorn`.

Runtime command:

```powershell
& "C:\Users\alesz\Projects_Apps\.venvs\ai-debug-assistant\Scripts\python.exe" -m uvicorn app.main:app --app-dir apps/api --reload
```

## API-Only Smoke Tests

- [x] Start API with `uvicorn`.
- [x] Validate `GET /api/v1/health`.
- [x] Validate `GET /api/v1/ready`.
- [x] Validate `GET /api/v1/metrics`.
- [x] Validate `POST /api/v1/query`.
- [x] Validate `POST /api/v1/evaluations/run` with `X-API-Key`.
- [x] Confirm evaluation response uses `weak_evidence_case_warning_rate`.
- [x] Confirm evaluation response uses `no_evidence_case_warning_rate`.
- [x] Confirm evaluation response returns `passed = true`.

## Auth Checks

- [x] Confirm protected endpoint returns `401` without `X-API-Key`.
- [x] Confirm protected endpoint succeeds with `X-API-Key: dev-local-key`.

## Full Local Platform Tests

These require Docker Desktop and the Compose stack.

- [x] Start `postgres`, `redis`, and `api` with Docker Compose.
- [x] Apply Alembic migrations against Compose Postgres.
- [x] Validate `GET /api/v1/health` reports PostgreSQL backend.
- [x] Validate `GET /api/v1/ready` reports database and Redis as available.
- [x] Start ingestion worker.
- [x] Enqueue document ingestion.
- [x] Validate ingestion job reaches `finished`.
- [x] Confirm `/api/v1/metrics` includes request, query, ingestion enqueue, and evaluation counters.
- [x] Confirm API logs include request IDs and runtime events.
- [x] Confirm worker logs include successful ingestion job events.

## Notes

- API-only mode can validate endpoint shape and evaluation behavior.
- Worker metrics are process-local; validate worker processing through worker logs and job status.
- Full platform mode is required before claiming local platform readiness for a fresh run.
- AWS readiness requires separate cloud smoke tests after Phase 8 infrastructure exists.

## Local Kubernetes Smoke Tests

These require the `kind` cluster, the locally built API image loaded into the cluster, and the Kubernetes manifests under `infra/k8s`.

- [x] Apply namespace, config, secret, PostgreSQL, Redis, API, worker, PVC, and Service manifests.
- [x] Run Alembic migration Job in Kubernetes.
- [x] Confirm PostgreSQL Pod is `Running` and `Ready`.
- [x] Confirm Redis Pod is `Running` and `Ready`.
- [x] Confirm API Pod is `Running` and `Ready`.
- [x] Confirm worker Pod is `Running`.
- [x] Confirm API readiness probe reports ready state.
- [x] Port-forward the API Service locally.
- [x] Validate `GET /api/v1/health` through Kubernetes.
- [x] Validate `GET /api/v1/ready` through Kubernetes.
- [x] Validate `GET /api/v1/metrics` through Kubernetes.
- [x] Validate `POST /api/v1/query` through Kubernetes.
- [x] Validate `POST /api/v1/evaluations/run` through Kubernetes.
- [x] Confirm protected route returns `401` in Kubernetes without `X-API-Key`.
- [x] Enqueue document ingestion through the Kubernetes-hosted API.
- [x] Validate ingestion job reaches `finished` in Kubernetes.
- [x] Confirm API logs include request IDs and runtime events in Kubernetes.
- [x] Confirm worker logs include successful ingestion events in Kubernetes.
- [x] Record one failed drill for a dependency-readiness path and capture the debugging commands used.

## Local Kubernetes Evidence Summary

Date: 2026-06-20

Runtime:

- local cluster: `kind`
- namespace: `ai-debug`
- image: `ai-debug-assistant-api:local`
- access path: `kubectl port-forward service/ai-debug-api 8000:8000 -n ai-debug`

Validated evidence:

- Alembic migration Job ran against PostgreSQL and reported `PostgresqlImpl`.
- `GET /api/v1/health` returned `status: ok` and `backend: postgresql`.
- `GET /api/v1/ready` returned `status: ok` with `runtime`, `database`, and `redis_queue` all healthy.
- `GET /api/v1/metrics` exposed request, readiness, query, ingestion, and evaluation counters from the Kubernetes-hosted API.
- `POST /api/v1/query` returned grounded output with citations, `retrieval_trace_id`, warnings, and latency.
- `POST /api/v1/evaluations/run` returned `passed: true` with expected threshold fields.
- protected route auth succeeded with `X-API-Key: dev-local-key`.
- protected route auth failed without `X-API-Key` and returned `Missing or invalid API key.`
- ingestion worker logged `worker.started`, `ingestion.job.started`, and `ingestion.job.succeeded`.
- API logs included structured JSON records with `request_id`, `http.request.completed`, and `readiness.checked`.

## Local Kubernetes Failure Drill

Date: 2026-06-20

Scenario:

- simulate Redis dependency loss and confirm readiness degrades without killing the API process

Commands used:

```powershell
kubectl scale deployment redis --replicas=0 -n ai-debug
Invoke-RestMethod http://127.0.0.1:8000/api/v1/ready
kubectl scale deployment redis --replicas=1 -n ai-debug
Invoke-RestMethod http://127.0.0.1:8000/api/v1/ready
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
```

Observed behavior:

- when Redis was scaled to `0`, `/api/v1/ready` returned `status: degraded`
- degraded dependency detail showed `redis_queue: unavailable`
- the API process stayed alive and `/api/v1/health` remained an appropriate liveness signal
- after Redis was restored, `/api/v1/ready` returned `status: ok` again with `redis_queue: ok`

Operational lesson:

- dependency loss should normally change readiness first
- Kubernetes should stop routing traffic to an unready Pod before we consider restarting the process
