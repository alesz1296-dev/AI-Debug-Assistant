# Phase 5 Tasks: Observability

## Status

Complete. Structured logging, request IDs, readiness, metrics, and local observability proof are in place.

## Post-Completion Hardening

- [x] Add separate readiness degradation counters.
- [x] Add explicit worker job success/failure logs by ingestion kind.
- [ ] Optionally add histogram-style latency buckets later.
- [ ] Optionally add per-job worker timing later.

## Session 1: Logging Foundation

- [x] Add structured logging configuration.
- [x] Use stable event names for runtime startup, query, ingestion, evaluation, and queue errors.
- [x] Include backend name and environment in runtime/startup logs.
- [x] Add tests or focused assertions where logging behavior is deterministic.

## Session 2: Request IDs And API Middleware

- [x] Add request ID middleware.
- [x] Accept inbound `X-Request-ID` when provided.
- [x] Generate a request ID when the client does not provide one.
- [x] Return the request ID in response headers.
- [x] Include request ID, method, path, status code, and latency in structured request logs.
- [x] Add tests for generated and propagated request IDs.

## Session 3: Health And Readiness

- [x] Keep `/api/v1/health` lightweight for process liveness.
- [x] Add `/api/v1/ready` for dependency-aware readiness.
- [x] Check runtime initialization in readiness.
- [x] Check database reachability in readiness.
- [x] Report Redis queue availability in readiness without making health depend on Redis.
- [x] Add tests for healthy and degraded readiness behavior.

## Session 4: Metrics And Local Proof

- [x] Add metrics endpoint or exporter.
- [x] Track request count and request latency.
- [x] Track query count, query latency, retrieval hit count, and confidence/score summary.
- [x] Track ingestion enqueue success and queue-unavailable failures.
- [x] Track evaluation run count and pass/fail count.
- [x] Track weak-evidence and no-evidence warning counts.
- [x] Update demo script with local observability proof.
- [x] Update README and architecture docs with observability run commands.
