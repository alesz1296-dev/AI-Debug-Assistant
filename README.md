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

This repository has reached the DevOps-ready local platform milestone.

That means the app is persistent, observable, containerized, tested, documented, and validated locally with API, Postgres, Redis, worker processing, endpoint checks, and CI build checks.

It is not AWS-ready or cloud-deployed yet. Cloud infrastructure, deployment workflow, secrets handling, cloud logs/metrics, and teardown documentation belong to Phase 8.

## SSD Phase Roadmap

The project is governed by the phase map in `specs/README.md`.

Current completed milestone: Phase 7 - DevOps-ready milestone and hardening.

Current implementation phase: Phase 8 - local Kubernetes first, then cost-controlled AWS Terraform, EKS labs, Helm, and cloud deployment workflow.

- Phase 0: Local MVP baseline.
- Phase 1: SSD planning hardening.
- Phase 2: PostgreSQL persistence and pgvector retrieval.
- Phase 3: Redis/RQ ingestion workers.
- Phase 4: evaluation quality gates.
- Phase 5: observability.
- Phase 6: container and CI validation.
- Phase 7: DevOps-ready milestone and hardening.
- Phase 8: local Kubernetes, AWS Terraform, short-lived EKS labs, Helm, and cloud deployment.
- Phase 9: optional dashboard.

The Phase 8 local Kubernetes path starts with `kind`; see `docs/local-kubernetes-kind.md`.

For AWS image publishing, use the local ECR helper from the repository root:

```powershell
.\scripts\push-api-image-to-ecr.ps1
```

The script uses AWS CLI identity and temporary ECR login tokens; it does not store AWS secrets in the repository.

Current Phase 8 progress:

- local `kind` cluster created and validated
- local API image built and loaded into the cluster
- Kubernetes foundation manifests created under `infra/k8s`
- PostgreSQL and Redis deployed in the `ai-debug` namespace
- PostgreSQL persistence added with a PVC template
- local Kubernetes runtime validation completed with API, worker, logs, metrics, auth, ingestion, and a Redis readiness failure drill
- Helm chart added under `infra/helm/ai-debug-assistant`
- automated `kind` smoke validation added to CI for the Helm-installed stack
- Stage 8A local Kubernetes is complete
- Stage 8B AWS/Terraform planning is complete
- Stage 8C AWS implementation is active with a cost-controlled `dev` baseline
- Terraform bootstrap, `dev` network, ECR, and EKS module wiring are in place
- EKS is disabled by default and used only for short-lived AWS-specific labs
- NAT Gateway is disabled by default and enabled only when a lab requires private-subnet outbound access
- RDS, ElastiCache, ALB, and Container Insights are planned as opt-in future labs, not default `dev` resources
- default AWS `dev` has been validated with `terraform validate` and a no-change `terraform plan`
- manual API image build, tag, push, and ECR lookup have been validated against the `dev` ECR repository
- `scripts/push-api-image-to-ecr.ps1` now captures the repeatable local ECR publishing flow

## Core Capabilities

- FastAPI API for incident triage queries, health checks, readiness checks, and evaluations.
- Retrieval-augmented answer generation over public and synthetic operational evidence.
- Grounded responses with citations, confidence, warnings, and suggested next steps.
- PostgreSQL-backed persistence with pgvector-ready retrieval.
- Redis/RQ worker boundary for asynchronous ingestion.
- Evaluation harnesses for retrieval quality, groundedness, citation presence, warning behavior, and latency.
- Structured logs, request IDs, readiness signals, and Prometheus-style metrics.
- Docker Compose, local Kubernetes, Helm, and Terraform foundations for progressive platform delivery.

## Project Documentation

The repository uses Spec-Driven Development artifacts under `specs/` to describe phase goals, implementation plans, and verifiable task lists. Operational runbooks live under `docs/` and cover validation, architecture, data policy, local Kubernetes, AWS cost control, and deployment evidence.

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
- `GET http://127.0.0.1:8000/api/v1/ready`
- `GET http://127.0.0.1:8000/api/v1/metrics`
- `POST http://127.0.0.1:8000/api/v1/query`

The health response stays lightweight and reports the active backend as `postgresql`, `sqlite`, or `sqlite_fallback`.
The readiness response reports `ok` or `degraded` based on runtime initialization, database reachability, and Redis queue availability.

Structured JSON logs are enabled through `structlog`. Use `LOG_LEVEL=INFO` by default, or set a different level in `.env` for local debugging.
The metrics endpoint exposes a Prometheus-style text surface for local request, readiness, query, ingestion, and evaluation signals.

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

If you want the app to keep running without Postgres during local development, set `ALLOW_SQLITE_FALLBACK=true` explicitly. Otherwise startup will fail fast when the configured Postgres database is unavailable.

Evaluation runs now return pass/fail status, threshold values, citation presence rate, latency, and warning rates. When the active retriever is database-backed, those evaluation runs are also persisted for later audit.

## Phase 6 Validation Status

Phase 6 is complete. The local Docker/Compose runtime, migration path, endpoint behavior, and CI checks have been validated together.

Validated so far:

- `docker compose -f infra/docker-compose.yml ps` shows `api`, `postgres`, and `redis` as `Up`.
- The API image has been used to run Alembic successfully through `0003_enable_vector`.
- `GET /api/v1/health` returns `status: ok` with `backend: postgresql`.
- `GET /api/v1/ready` returns `status: ok` with `runtime`, `database`, and `redis_queue` all reporting `ok`.
- `GET /api/v1/metrics` returns a Prometheus-style metrics surface with live request and readiness counters.
- `POST /api/v1/query` succeeds in the containerized stack and returns a grounded response with citations, warnings, `retrieval_trace_id`, and latency.
- Query-path stability now depends on the validated `vector` extension migration and retrieval-session rollback handling after database errors.

CI now validates the Python and container delivery path in sequence:

- dependency install
- `ruff check .`
- `mypy apps/api/app apps/api/tests`
- `pytest -q`
- `docker compose -f infra/docker-compose.yml build api`

## Current CI Coverage

The current GitHub Actions workflow satisfies the Phase 7 local-platform validation target.

Present in CI today:

- dependency install
- `ruff check .`
- `mypy apps/api/app apps/api/tests`
- `pytest -q`
- sequential `docker compose -f infra/docker-compose.yml build api`
- `scripts/ci_compose_smoke.py`, which builds the API image, starts Postgres and Redis, waits for Postgres readiness, applies Alembic migrations, starts the API, validates `/health`, `/ready`, `/metrics`, `/query`, and `/evaluations/run`, processes a Redis/RQ ingestion job with a burst worker, validates API logs, validates worker success logs, and tears down the isolated smoke stack.
- `scripts/ci_k8s_smoke.py`, which builds the API image, creates a fresh `kind` cluster, renders and installs the Helm chart, waits for PostgreSQL, Redis, API, worker, and migration readiness, validates `/health`, `/ready`, `/metrics`, `/query`, `/evaluations/run`, checks protected-route auth failure, validates ingestion completion, validates API logs, validates worker logs, and deletes the cluster.

## Phase 7 Validation Status

Phase 7 is complete. The project is now DevOps-ready as a local platform and ready to begin Phase 8 cloud planning.

Validated Phase 7 evidence:

- Phases 0 through 6 are complete and documented.
- CI passes install, Ruff, mypy, pytest, and sequential Docker Compose API image build validation.
- The local Compose stack runs API, Postgres, and Redis.
- The API reports PostgreSQL-backed health and dependency-aware readiness.
- A temporary worker processed a Redis/RQ document ingestion job to `finished`.
- `/api/v1/metrics` exposes request, readiness, query, ingestion, worker, and evaluation counters.
- `/api/v1/evaluations/run` passes the golden local evaluation suite after the rebuilt API image.
- API logs include `runtime.started`, `readiness.checked`, `query.completed`, `ingestion.queued`, and `evaluation.completed`.
- Worker logs include `ingestion.job.succeeded`.

Phase 7 does not create AWS resources, Terraform modules, Kubernetes manifests, or deployment automation. Those are Phase 8 responsibilities.

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

   The Docker Compose project is named `ai-debug-assistant`, so that is the name you should expect to see in Docker Desktop rather than a generic label like `infra`.

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

If Redis is unavailable, ingestion endpoints and job-status lookup now return `503` with a structured `queue_unavailable` error instead of a raw server exception.

## Local Observability Proof

1. Start the API and worker with the local infrastructure services running.
2. Call `/api/v1/health`, `/api/v1/ready`, and `/api/v1/query`.
3. Run `/api/v1/evaluations/run` with the API key.
4. Open `/api/v1/metrics` and confirm request, query, ingestion, and evaluation counters are present.
5. Confirm readiness metrics include `enterprise_ai_readiness_checks_total` and, when degraded, `enterprise_ai_readiness_degraded_total`.
6. Review the JSON logs for `runtime.started`, `http.request.completed`, `query.completed`, `evaluation.completed`, `readiness.checked`, `ingestion.job.succeeded`, and `ingestion.job.failed`.

## Optional Observability Follow-Ups

- Add histogram-style latency buckets if we later want a more serious metrics surface than sum/count pairs.
- Add more readiness-degradation detail if container/runtime failure modes become more varied in Phase 6 or later.
- Expand worker observability with per-job timing if background ingestion becomes a stronger performance concern.

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

