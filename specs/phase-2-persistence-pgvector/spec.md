# Phase 2 Spec: Persistence + pgvector

## Goal

Replace in-memory-only state with durable PostgreSQL persistence and vector-backed retrieval.

## Requirements

- Persist debug cases, documents, logs, embeddings, retrieval traces, and evaluation runs.
- Use pgvector or an equivalent PostgreSQL vector capability for retrieval.
- Preserve the existing query response shape unless a later spec explicitly changes it.
- Data must survive process restart.

## Acceptance Criteria

- Seeded and ingested records are stored in PostgreSQL.
- Query retrieval uses persisted vector records instead of process memory.
- Tests prove data survives app restart or retriever reconstruction.
- Documentation describes the storage model and migration path.

## Out Of Scope

- AWS-managed database provisioning.
- Kubernetes deployment.
- Dashboard UI.
