# Phase 3 Spec: Ingestion Workers

## Goal

Move ingestion work that can outgrow the request path into a Redis/RQ worker boundary.

## Status

Complete. The queue boundary, failure visibility, tests, and local run guidance are in place.

## Requirements

- API endpoints enqueue ingestion work instead of doing all processing inline.
- Workers process document, log, and debug-case ingestion jobs.
- Failed jobs are observable enough for local debugging.
- Ingestion behavior remains safe for public/synthetic data only.

## Acceptance Criteria

- Ingestion jobs can be queued and processed locally.
- Tests cover enqueue behavior and worker processing.
- Failed ingestion has a visible status or error path.
- Documentation explains local worker startup.

## Out Of Scope

- Managed cloud queues.
- Autoscaling workers.
- Dashboard job management.
