# Phase 0 Plan: Local MVP Baseline

## Technical Approach

Start with a local deterministic RAG implementation to prove API contracts, data safety, tests, and learning flow. Keep the retrieval service boundary narrow so PostgreSQL + pgvector can replace the in-memory implementation later.

The current implementation is intentionally below deployment-ready standard. It is a validated local slice, not a cloud-ready service yet.

## Current Slice

- FastAPI app with public and protected routes.
- Deterministic hashing embeddings.
- Seeded synthetic incidents, logs, and runbooks.
- Grounded answer composer with citations and weak-evidence warnings.
- Evaluation harness for golden synthetic cases.
- CI-ready tests.

## Deployment Readiness Bar

Do not label the project deployment-ready or DevOps-ready until the following are implemented and documented:

- persistent database or storage for records and ingestion data
- non-memory retrieval path
- vector retrieval backend
- container build and run path
- automated CI checks for test, lint, and build
- infrastructure as code for cloud resources
- logging and metrics suitable for runtime inspection
- a repeatable deployment procedure
- a documented operational demo path

## Later Slices

- PostgreSQL schema and Alembic migrations.
- pgvector storage and retrieval.
- Redis/RQ background ingestion jobs.
- OpenTelemetry instrumentation.
- React dashboard.
- Cloud deployment.

These slices are now governed by the phase map in `specs/README.md`.

