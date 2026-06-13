# Phase 0 Plan: Local MVP Baseline

## Technical Approach

Start with a local deterministic RAG implementation to prove API contracts, data safety, tests, and learning flow. Keep the retrieval service boundary narrow so PostgreSQL + pgvector can replace the in-memory implementation later.

The Phase 0 implementation was intentionally below deployment-ready standard. Later phases have now promoted the project to a DevOps-ready local platform, but it is still not a cloud-ready service.

## Current Slice

- FastAPI app with public and protected routes.
- Deterministic hashing embeddings.
- Seeded synthetic incidents, logs, and runbooks.
- Grounded answer composer with citations and weak-evidence warnings.
- Evaluation harness for golden synthetic cases.
- CI-ready tests.

## Deployment Readiness Bar

The local DevOps readiness bar is now met through Phase 7. The remaining deployment-readiness work is cloud-specific and belongs to Phase 8.

- [x] persistent database or storage for records and ingestion data
- [x] non-memory retrieval path
- [x] vector retrieval backend
- [x] container build and run path
- [x] automated CI checks for test, lint, type checks, and build
- [x] logging and metrics suitable for runtime inspection
- [x] documented local operational demo path
- [ ] infrastructure as code for cloud resources
- [ ] repeatable cloud deployment procedure
- [ ] deployed operational demo path

## Later Slices

- PostgreSQL schema and Alembic migrations.
- pgvector storage and retrieval.
- Redis/RQ background ingestion jobs.
- local observability instrumentation.
- React dashboard.
- Cloud deployment.

These slices are now governed by the phase map in `specs/README.md`.

