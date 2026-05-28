# Phase 3 Plan: Ingestion Workers

## Status

Complete. The job contract, worker entrypoint, queue path for document and log ingestion, debug-case queue path, local job-status visibility, and local run docs are in place.

## Approach

Use Redis and RQ, already declared in project dependencies, to create a simple local worker model. Keep synchronous test helpers where useful, but make the production path queue-backed.

## Data Flow

API receives ingestion request, validates payload, enqueues job, worker stores records and embeddings, API exposes enough status for local verification.

Current implementation note: document and log ingestion are now queued through Redis/RQ, and debug-case creation also enqueues a background indexing job while preserving the immediate debug-case response shape.

Local failure visibility is exposed through `GET /api/v1/ingestion-jobs/{job_id}`, which reports `queued`, `started`, `finished`, `failed`, or `not_found` and surfaces the failure type/message when available.

## Validation

- Tests for queue submission.
- Tests for worker job execution.
- Manual local verification with API, Redis, and worker process.
