# Phase 2 Tasks: Persistence + pgvector

## Status

Complete. All listed implementation tasks are checked off, and the Alembic migration has been applied against the compose Postgres service.

## Chunk 1: Durable Records And Seeding

- [x] Add database package with SQLAlchemy base, session, models, and initialization helper.
- [x] Add durable `knowledge_records` table model.
- [x] Add repository for upserting, loading, counting, and listing knowledge records.
- [x] Add idempotent seed helper for the current public/synthetic seed records.
- [x] Add tests for idempotent seeding and durable record lookup.
- [x] Run tests, lint, and type checks after the durable-records chunk.

## Remaining Phase 2 Work

- [x] Define PostgreSQL tables for records, embeddings, and retrieval traces.
- [x] Persist embeddings for seeded knowledge records.
- [x] Persist retrieval traces and ranked hits.
- [x] Add tests for embedding persistence and retrieval trace persistence.
- [x] Introduce database retriever with pgvector-backed PostgreSQL search path.
- [x] Add portable fallback tests for database retriever behavior.
- [x] Implement database-backed record ingestion.
- [x] Switch the live API query path to database-backed retrieval.
- [x] Preserve the current query API response shape.
- [x] Add tests for persistence and retrieval.
- [x] Update architecture docs with current and target storage behavior.
- [x] Define PostgreSQL table for evaluation runs.
- [x] Add migration workflow.
