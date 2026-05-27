# Phase 2 Tasks: Persistence + pgvector

## Chunk 1: Durable Records And Seeding

- [x] Add database package with SQLAlchemy base, session, models, and initialization helper.
- [x] Add durable `knowledge_records` table model.
- [x] Add repository for upserting, loading, counting, and listing knowledge records.
- [x] Add idempotent seed helper for the current public/synthetic seed records.
- [x] Add tests for idempotent seeding and durable record lookup.
- [x] Run tests, lint, and type checks after the durable-records chunk.

## Remaining Phase 2 Work

- [ ] Define PostgreSQL tables for records, embeddings, retrieval traces, and evaluation runs.
- [ ] Add migration workflow.
- [ ] Implement database-backed record ingestion.
- [ ] Implement pgvector-backed similarity search.
- [ ] Preserve the current query API response shape.
- [ ] Add tests for persistence and retrieval.
- [ ] Update architecture docs with current and target storage behavior.
