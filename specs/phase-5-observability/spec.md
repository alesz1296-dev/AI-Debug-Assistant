# Phase 5 Spec: Observability

## Goal

Make the service inspectable during local and deployed operation through logs, metrics, traces, health, and readiness.

## Requirements

- Add structured logs for query, ingestion, retrieval, evaluation, and errors.
- Add request identifiers.
- Expose latency, retrieval, evaluation, and error metrics.
- Add readiness behavior separate from basic health.
- Use `structlog` and OpenTelemetry unless a later decision replaces them.
- Keep cloud dashboards, alerting, and managed observability services out of Phase 5.

## Acceptance Criteria

- Local run shows structured logs for main workflows.
- Every HTTP response includes a request ID.
- Request logs include method, path, status code, latency, and request ID.
- Metrics expose request latency and retrieval/evaluation signals.
- Health and readiness endpoints are separate, documented, and tested.
- Readiness can report dependency degradation without pretending the service is fully ready.
- Observability docs explain how to prove the service is alive and useful.

## Out Of Scope

- Managed Grafana.
- Cloud log aggregation.
- Distributed tracing across external systems.
