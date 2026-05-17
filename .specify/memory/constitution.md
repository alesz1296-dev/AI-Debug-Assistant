# Project Constitution

## Principles

1. Public-data-only engineering.
   No company logs, private stack traces, customer data, copied internal runbooks, or secrets may be used.

2. Specifications are the source of truth.
   Each feature starts with intent, acceptance criteria, test expectations, and explicit data-safety constraints.

3. Grounded AI over fluent AI.
   Debug answers must include citations, confidence, warnings when evidence is weak, and concrete next steps.

4. Production habits from day one.
   Every stage must improve testability, observability, security posture, or deployability.

5. Learning is part of the deliverable.
   Private `.learning/` notes explain fundamentals, tradeoffs, mistakes, and hands-on exercises.

## Quality Gates

- Tests pass before a task is considered complete.
- Seed/demo data is synthetic, public, or locally generated.
- APIs preserve response fields: answer, hypotheses, citations, confidence, retrieval_trace_id, model, latency_ms, warnings, next_steps.
- Implementation can run locally without paid APIs.

