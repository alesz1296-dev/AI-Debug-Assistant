# Implementation Plan

## Technical Approach

Start with a local deterministic RAG implementation to prove API contracts, data safety, tests, and learning flow. Keep the retrieval service boundary narrow so PostgreSQL + pgvector can replace the in-memory implementation later.

## Current Slice

- FastAPI app with public and protected routes.
- Deterministic hashing embeddings.
- Seeded synthetic incidents, logs, and runbooks.
- Grounded answer composer with citations and weak-evidence warnings.
- Evaluation harness for golden synthetic cases.
- CI-ready tests.

## Later Slices

- PostgreSQL schema and Alembic migrations.
- pgvector storage and retrieval.
- Redis/RQ background ingestion jobs.
- OpenTelemetry instrumentation.
- React dashboard.
- Cloud deployment.

