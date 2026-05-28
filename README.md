# Enterprise AI Debug Assistant

Production-minded AI Engineering portfolio project built with Spec-Driven Development.

This assistant investigates public or synthetic operational incidents by combining:

- public log datasets such as Loghub-style logs,
- public incident postmortem summaries,
- public technical documentation,
- deterministic local retrieval for development and tests,
- a future-ready boundary for PostgreSQL + pgvector, workers, observability, and deployment.

No company data belongs in this repository.

## Readiness Status

This repository currently contains a working local-first slice, not a deployment-ready or DevOps-ready system.

Deployment and DevOps readiness are intentionally gated by `specs/001-enterprise-ai-debug-assistant/spec.md` and `specs/001-enterprise-ai-debug-assistant/tasks.md`.

Until those gates are complete, the project should be treated as a validated prototype rather than a cloud-deployable service.

## SSD Phase Roadmap

The project is governed by the phase map in `specs/README.md`.

Current planning milestone: Phase 3 - Redis/RQ ingestion workers is complete.

Next implementation phase: Phase 4 - evaluation quality gates.

- Phase 0: Local MVP baseline.
- Phase 1: SSD planning hardening.
- Phase 2: PostgreSQL persistence and pgvector retrieval.
- Phase 3: Redis/RQ ingestion workers.
- Phase 4: evaluation quality gates.
- Phase 5: observability.
- Phase 6: container and CI validation.
- Phase 7: DevOps-ready milestone and manual-development handoff.
- Phase 8: AWS, Kubernetes, Terraform, and cloud deployment.
- Phase 9: optional dashboard.

## What It Demonstrates

- FastAPI service design
- RAG ingestion and retrieval
- grounded answers with citations
- synthetic benchmark cases
- evaluation harnesses
- production data-safety rules
- observability and security scaffolding
- private learning notes excluded from Git

## Documentation Policy

Public SSD docs are tracked in git. Private learning notes, coaching notes, scratch plans, and manual-development logs belong in ignored folders such as `.learning/`, `.planning/`, or `.private-notes/`.

## Deferred Frameworks

LangChain and LangGraph are intentionally not part of the current stack. They may be added later only if we have a concrete workflow that benefits from a higher-level orchestration or tool abstraction layer.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir apps/api --reload
```

Then open:

- `GET http://127.0.0.1:8000/api/v1/health`
- `POST http://127.0.0.1:8000/api/v1/query`

For local protected routes, use:

```text
X-API-Key: dev-local-key
```

## Example Query

```json
{
  "question": "The API is timing out and workers are backing up after a deploy. What should I check?",
  "collections": ["incident_cases", "system_logs", "knowledge_base"],
  "top_k": 5
}
```

## Migration Workflow

Use Alembic for schema changes:

```bash
alembic -c alembic.ini upgrade head
alembic -c alembic.ini revision --autogenerate -m "describe change"
```

The current migration path has been validated against the compose Postgres service using the API image and `alembic upgrade head`.

## Local Ingestion Worker

When Redis is running locally, the ingestion worker can be started with:

```powershell
python -m app.workers.ingestion
```

The API now enqueues document and log ingestion jobs instead of processing them inline. Debug-case creation also queues a background indexing job while keeping the immediate debug-case response shape.

For a full local worker loop:

1. Start the infrastructure services:

   ```powershell
   docker compose -f infra/docker-compose.yml up -d postgres redis
   ```

2. Start the API:

   ```powershell
   python -m uvicorn app.main:app --app-dir apps/api --reload
   ```

3. Start the worker in a second terminal:

   ```powershell
   python -m app.workers.ingestion
   ```

4. Enqueue a document or log via the API, then inspect the job:

   ```text
   GET /api/v1/ingestion-jobs/{job_id}
   ```

The job status endpoint reports queued, started, finished, failed, or not found, and exposes the failure type/message when a job crashes locally.

## Data Policy

Allowed:

- public datasets,
- public incident reports,
- public documentation,
- synthetic incidents,
- logs from local demo applications.

Forbidden:

- company logs,
- private stack traces,
- customer data,
- copied internal runbooks,
- secrets or tokens.

See [docs/data-policy.md](docs/data-policy.md).

