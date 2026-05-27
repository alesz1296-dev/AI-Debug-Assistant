# Phase 5 Spec: Observability

## Goal

Make the service inspectable during local and deployed operation through logs, metrics, traces, health, and readiness.

## Requirements

- Add structured logs for query, ingestion, retrieval, evaluation, and errors.
- Add request identifiers.
- Expose latency, retrieval, evaluation, and error metrics.
- Add readiness behavior separate from basic health.
- Use `structlog` and OpenTelemetry unless a later decision replaces them.

## Acceptance Criteria

- Local run shows structured logs for main workflows.
- Metrics expose request latency and retrieval/evaluation signals.
- Health and readiness endpoints are documented and tested.
- Observability docs explain how to prove the service is alive and useful.

## Out Of Scope

- Managed Grafana.
- Cloud log aggregation.
- Distributed tracing across external systems.
