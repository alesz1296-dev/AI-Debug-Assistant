# Phase 3 Plan: Ingestion Workers

## Approach

Use Redis and RQ, already declared in project dependencies, to create a simple local worker model. Keep synchronous test helpers where useful, but make the production path queue-backed.

## Data Flow

API receives ingestion request, validates payload, enqueues job, worker stores records and embeddings, API exposes enough status for local verification.

## Validation

- Tests for queue submission.
- Tests for worker job execution.
- Manual local verification with API, Redis, and worker process.
