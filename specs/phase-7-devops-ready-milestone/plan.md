# Phase 7 Plan: DevOps-Ready Milestone

## Approach

Use this phase as a gate, not a large implementation phase. Review evidence from earlier phases and decide whether the system is ready to become the cloud/DevOps showcase.

## Development Mode

After this milestone, the project owner manually implements more of the system. Codex remains an architectural guide, reviewer, debugging partner, and implementation coach.

## Validation

- Review all prior acceptance criteria.
- Confirm private notes are ignored.
- Confirm public docs describe the manual-development transition.
- Confirm the next cloud phase has clear boundaries.

## Completed Evidence

- Phases 0 through 6 are complete and publicly documented.
- CI validates install, Ruff, mypy, pytest, and sequential Docker Compose API image build.
- Local Compose starts API, Postgres, and Redis.
- Alembic migration path is validated through `0003_enable_vector`.
- Runtime endpoints `/health`, `/ready`, `/metrics`, `/query`, and `/evaluations/run` work against the PostgreSQL-backed API.
- Worker validation processed a Redis/RQ document ingestion job to `finished`.
- Observability proof includes request, readiness, query, ingestion, worker, and evaluation metrics plus stable API and worker log events.

## Phase 7 Validation Commands

Use the local Docker stack and API key:

```powershell
docker compose -f infra/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml ps
docker compose -f infra/docker-compose.yml build api
docker compose -f infra/docker-compose.yml up -d --force-recreate api
```

Validate API runtime:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/ready
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/query -ContentType "application/json" -Body '{"question":"The API is timing out and the Redis queue is growing after a deploy."}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/evaluations/run -Headers @{"X-API-Key"="dev-local-key"}
Invoke-WebRequest http://127.0.0.1:8000/api/v1/metrics -UseBasicParsing
```

Validate worker path by running a temporary worker on the Compose network, enqueueing a document through `/api/v1/documents`, polling `/api/v1/ingestion-jobs/{job_id}` until `finished`, and checking `/metrics` plus worker logs for ingestion counters and `ingestion.job.succeeded`.

## Boundary To Phase 8

Phase 7 proves local DevOps readiness. It does not create Terraform, AWS resources, Kubernetes manifests, registry publishing, cloud secrets, or cloud deployment automation.
