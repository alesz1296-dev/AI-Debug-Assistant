# Architecture

## Current State

```mermaid
flowchart LR
    Client["Client or Portfolio Demo"] --> API["FastAPI API"]
    API --> Auth["API Key Guard"]
    API --> Ingest["Ingestion + Retrieval Service"]
    API --> RAG["Grounded Debug Assistant"]
    Ingest --> Store["PostgreSQL / SQLite runtime store"]
    RAG --> Store
    RAG --> Eval["Evaluation Harness"]
    Store --> Cases["incident_cases"]
    Store --> Logs["system_logs"]
    Store --> KB["knowledge_base"]
```

The current implementation boots a runtime database-backed retriever on application startup. For PostgreSQL, startup applies Alembic migrations before seeding and serving requests. For SQLite, startup uses the `create_all()` fallback for lightweight local development and tests. In both cases, it persists knowledge records, deterministic embeddings, retrieval traces, and evaluation runs. Document and log ingestion now enqueue Redis/RQ jobs, and debug-case creation also emits a background indexing job while keeping the immediate debug-case response shape.

## Target State

```mermaid
flowchart LR
    Client["Client or Portfolio Demo"] --> API["FastAPI API"]
    API --> Auth["API Key Guard"]
    API --> Query["Query Service"]
    API --> IngestAPI["Ingestion API"]
    IngestAPI --> Queue["Redis / RQ Queue"]
    Queue --> Worker["Ingestion Worker"]
    Worker --> DB["PostgreSQL + pgvector"]
    Query --> DB
    Query --> Eval["Evaluation Harness"]
    API --> Obs["Logs / Metrics / Traces"]
    Worker --> Obs
    Eval --> Obs
```

The target platform persists records and embeddings, uses pgvector retrieval, moves ingestion through workers, exposes observable runtime signals, and can later be deployed through CI/CD and AWS infrastructure.

If the project later needs multi-step stateful incident triage, LangGraph is the likely candidate for the orchestration layer. If the team later wants provider or tool abstraction, LangChain is the likely candidate. For now, both are intentionally out of scope so the platform stays auditable and easy to reason about.

## Retrieval Collections

- `incident_cases`: synthetic incidents and public postmortem summaries.
- `system_logs`: Loghub-style public logs and local demo app logs.
- `knowledge_base`: public docs, runbooks, and project notes.

## Current Implementation

The service boundary is intentionally small, but the live app now uses the database-backed retriever behind the same API response shape. The Docker, compose, and CI files are still scaffold until Phase 6 validates them as accepted platform assets.

