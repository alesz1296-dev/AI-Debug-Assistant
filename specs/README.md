# SSD Phase Map

This directory governs the Enterprise AI Debug Assistant as a small production-grade AI platform.

The project must not claim deployment readiness, DevOps readiness, or cloud readiness until the relevant phase acceptance criteria are met. Each phase owns three public SSD artifacts:

- `spec.md`: goals, requirements, constraints, out-of-scope boundaries, and acceptance criteria.
- `plan.md`: implementation approach, architectural decisions, data flow, and risk notes.
- `tasks.md`: restrictive, verifiable work items.

## Current Milestone

Phase 7 - DevOps-ready milestone is complete.

Next implementation phase: Phase 8 - local Kubernetes first, then AWS EKS, Terraform, and cloud deployment planning.

## End Goal

Build a deployable, observable AI debugging assistant that ingests public/synthetic operational evidence, stores and retrieves it with PostgreSQL and pgvector, processes ingestion through workers, evaluates grounded triage quality, and can later be ported to AWS as a CI/CD and DevOps portfolio showcase.

## Phase Order

1. `001-enterprise-ai-debug-assistant`: Phase 0 - Local MVP Baseline.
2. `phase-1-ssd-planning-hardening`: SSD planning hardening.
3. `phase-2-persistence-pgvector`: persistent storage and vector retrieval.
4. `phase-3-ingestion-workers`: asynchronous ingestion boundary.
5. `phase-4-evaluation-quality-gates`: evaluation thresholds and regression gates.
6. `phase-5-observability`: logs, metrics, traces, health, and readiness.
7. `phase-6-container-ci-validation`: container and CI validation.
8. `phase-7-devops-ready-milestone`: platform maturity milestone before cloud work.
9. `phase-8-cloud-aws-kubernetes-terraform`: local Kubernetes, AWS EKS, Terraform, Helm, and deployment workflows.
10. `phase-9-dashboard-optional`: optional portfolio dashboard.

## Working Rule

Complete phases in order unless a later phase needs a small planning clarification. Do not implement a later phase before the previous phase has documented exit criteria and validation evidence.

## Development Mode Transition

Phase 7 is the handoff milestone. After Phase 7, development shifts toward more manual implementation by the project owner, with Codex acting as an architectural guide, reviewer, debugging partner, and implementation coach. Private guidance notes belong in ignored folders such as `.learning/` or `.planning/`.

## Deferred Frameworks

LangChain and LangGraph stay out of the base stack for now. Treat them as optional future additions only if a later phase needs a clearer abstraction for provider wiring, retrieval tooling, or multi-step stateful orchestration.
