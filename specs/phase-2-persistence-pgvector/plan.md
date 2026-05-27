# Phase 2 Plan: Persistence + pgvector

## Approach

Introduce a database-backed retrieval layer while keeping the existing API contracts stable. Use PostgreSQL and pgvector locally through the existing compose scaffold before any cloud work.

The first implementation chunk adds durable knowledge records and idempotent seed behavior without switching query retrieval away from the current in-memory retriever yet.

## Interfaces

- Retrieval records must keep collection, title, source, text, tags, metadata, and embedding data.
- Query responses must still include answer, hypotheses, citations, confidence, trace id, model, latency, warnings, and next steps.
- Evaluation runs should become persistable records for later observability and dashboard phases.

## Validation

- Unit tests for storage and retrieval behavior.
- API tests for query and ingestion behavior.
- Restart-style test or retriever reconstruction test proving persistence.
