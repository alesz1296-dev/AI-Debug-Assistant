# Phase 7 Tasks: DevOps-Ready Milestone

- [x] Verify Phase 0 through Phase 6 acceptance criteria.
- [x] Confirm local platform run path works end to end.
- [x] Confirm CI validates the service.
- [x] Confirm CI validates the full Compose platform smoke path.
- [x] Confirm observability proof exists.
- [x] Confirm public docs do not claim AWS readiness.
- [x] Record the manual-development transition in public SSD docs.
- [x] Keep private guidance notes in ignored folders.

## Validation Evidence

- Local Docker Compose stack validated API, Postgres, and Redis as running.
- Rebuilt API image validated the current code path before final endpoint checks.
- Worker validation used a temporary worker container to process a Redis/RQ document ingestion job to `finished`.
- `/health`, `/ready`, `/query`, `/evaluations/run`, and `/metrics` were validated against the rebuilt API.
- Evaluation returned `passed = true` with five golden cases and no failures.
- Metrics included request, readiness, query, ingestion enqueue, worker processed, and evaluation counters.
- API logs included `runtime.started`, `readiness.checked`, `query.completed`, `ingestion.queued`, and `evaluation.completed`.
- Worker logs included `ingestion.job.succeeded`.
- CI Compose smoke validation builds the API image, starts Postgres and Redis, waits for Postgres readiness, applies Alembic migrations through `0004_native_vector_embeddings`, starts the API, validates `/health`, `/ready`, `/metrics`, `/query`, and `/evaluations/run`, processes a worker ingestion job in burst mode, checks API logs, checks worker success logs, and tears down the isolated smoke stack.
