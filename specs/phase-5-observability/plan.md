# Phase 5 Plan: Observability

## Approach

Add local observability before cloud observability. Keep the first implementation minimal but real: structured logs, request ids, metrics endpoint, and readiness checks.

## Signals

- Request count and latency.
- Retrieval hit count and score summary.
- Evaluation pass/fail summary.
- Ingestion success and failure.
- Health and readiness state.

## Validation

- Tests for health and readiness.
- Manual local proof of logs and metrics.
- Documentation updates for the operational demo.
