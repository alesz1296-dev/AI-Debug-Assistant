# Architecture

```mermaid
flowchart LR
    Client["Client or Portfolio Demo"] --> API["FastAPI API"]
    API --> Auth["API Key Guard"]
    API --> Ingest["Ingestion Service"]
    API --> RAG["Grounded Debug Assistant"]
    Ingest --> Store["Retrieval Store"]
    RAG --> Store
    RAG --> Eval["Evaluation Harness"]
    Store --> Cases["incident_cases"]
    Store --> Logs["system_logs"]
    Store --> KB["knowledge_base"]
```

## Retrieval Collections

- `incident_cases`: synthetic incidents and public postmortem summaries.
- `system_logs`: Loghub-style public logs and local demo app logs.
- `knowledge_base`: public docs, runbooks, and project notes.

## Current Implementation

The first implementation uses deterministic local embeddings and in-memory retrieval so the API and tests work immediately. The service boundary is intentionally small, making PostgreSQL + pgvector a later replacement rather than a rewrite.

