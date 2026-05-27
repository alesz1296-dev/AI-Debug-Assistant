# Phase 2 Plan: Persistence + pgvector

## Approach

Introduce a database-backed retrieval layer while keeping the existing API contracts stable. Use PostgreSQL and pgvector locally through the existing compose scaffold before any cloud work.

The first implementation chunk adds durable knowledge records and idempotent seed behavior without switching query retrieval away from the current in-memory retriever yet.

The second implementation chunk persists deterministic embeddings and retrieval traces. It still stores vectors in a portable JSON column for testability; pgvector-backed similarity search remains the next chunk.

The third implementation chunk introduces `DatabaseRetriever`. PostgreSQL uses the pgvector `<=>` distance operator for similarity search, while non-PostgreSQL tests use a deterministic portable cosine fallback.

## Interfaces

- Retrieval records must keep collection, title, source, text, tags, metadata, and embedding data.
- Query responses must still include answer, hypotheses, citations, confidence, trace id, model, latency, warnings, and next steps.
- Evaluation runs should become persistable records for later observability and dashboard phases.

## Validation

- Unit tests for storage and retrieval behavior.
- API tests for query and ingestion behavior.
- Restart-style test or retriever reconstruction test proving persistence.
