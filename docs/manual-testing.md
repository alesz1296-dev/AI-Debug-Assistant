# Manual Testing Checklist

Manual testing records runtime behavior that automated tests do not fully prove. Keep this file current when endpoint behavior, runtime dependencies, or validation commands change.

The GitHub Actions `compose-smoke` job mirrors the full local platform checks in CI.

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
