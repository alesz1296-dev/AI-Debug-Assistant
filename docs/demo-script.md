# Demo Script

## Local MVP Demo

Use `docs/manual-testing.md` to track manual endpoint and platform validation while running the demo.

1. Explain the data policy: no confidential company data.
2. Show the three retrieval collections.
3. Run the health endpoint.
4. Run the readiness endpoint and point out dependency-aware status.
5. Query: "The API is timing out and Redis queue depth is growing after a deploy."
6. Point to citations, confidence, warnings, and next steps.
7. Run the evaluation endpoint.
8. Open the metrics endpoint and show request, query, ingestion, and evaluation counters.
9. Point to the JSON logs for request IDs, runtime startup, query completion, readiness checks, and evaluation completion.
10. Explain the roadmap from local deterministic retrieval to pgvector, workers, and cloud observability.

## Future Cloud Demo

This demo is not available yet. It belongs after the DevOps-ready milestone and cloud phase.

1. Show CI results for lint, tests, type checks, and container build.
2. Show deployed health and readiness checks.
3. Show logs, metrics, and traces for a query.
4. Run an operational smoke test.
5. Explain Terraform-managed infrastructure and teardown.

