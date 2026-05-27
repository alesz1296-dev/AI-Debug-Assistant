# Phase 0 Spec: Local MVP Baseline

## User Story

As a system architect building a public portfolio, I want a local-first debug assistant that can ingest public/synthetic operational evidence and produce grounded triage guidance through a reproducible, safety-gated workflow, so the project has a trustworthy baseline before persistence, observability, DevOps, and cloud phases begin.

## Phase Goal

Prove the minimum local AI debugging workflow: safe data policy, FastAPI routes, deterministic retrieval, seeded evidence, grounded responses, and local tests.

## Functional Requirements

- Create synthetic debug cases.
- Ingest public documentation, public postmortem summaries, and public/demo logs.
- Retrieve relevant evidence from incident cases, system logs, and knowledge base material.
- Generate a grounded response with hypotheses, citations, confidence, warnings, and next steps.
- Run an evaluation suite over golden synthetic cases.
- Enforce API-key protection for mutating/admin endpoints.

## Deployment-Ready Requirements

Phase 0 is not deployment-ready. The project is not deployment-ready until later phases prove all of these:

- Persistent storage exists for records and ingestion data.
- Retrieval no longer depends on in-memory state.
- A real vector-backed retrieval path exists, even if it starts as a local development implementation.
- Ingestion work that can outgrow the request path runs in a worker or queue boundary.
- The app runs in a container with the same command path used in local or cloud deployment.
- CI runs tests and build checks automatically on every change.
- The service exposes health and readiness signals suitable for orchestration.
- Logging and metrics are available for deployed runs.
- Cloud infrastructure is defined as code, not manual-only setup.

## DevOps-Ready Requirements

Phase 0 is not DevOps-ready. The project is not DevOps-ready until later phases prove all of these:

- A reproducible local environment exists from a clean checkout.
- Build, test, and lint steps are scripted and repeatable.
- Container images can be built and validated in CI.
- Deployable configuration is separated from application code.
- Cloud resources are provisionable through Terraform or an equivalent IaC layer.
- The deployment target can be recreated without manual click-through setup.
- The repo includes an operational demo path that proves the service is observable after deployment.

## Non-Functional Requirements

- Local development must work without external AI providers.
- Data safety must be testable in CI.
- Interfaces must remain compatible with a future PostgreSQL + pgvector backend.
- The project must be portfolio-readable with clear documentation.
- Deployment and DevOps readiness are gated by the checklist in `tasks.md`.

## Acceptance Criteria

- `GET /api/v1/health` returns service status.
- `POST /api/v1/query` returns the complete AI response shape.
- Protected ingestion/evaluation endpoints reject missing API keys.
- Evaluation returns retrieval and groundedness metrics.
- Tests pass with the local deterministic retrieval implementation.
- The repository explicitly records what is still missing before deployment readiness is claimed.

## Out Of Scope

- Persistent storage.
- pgvector retrieval.
- Background ingestion workers.
- Cloud infrastructure.
- Kubernetes deployment.
- Production observability.

