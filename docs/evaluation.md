# Evaluation Plan

## Metrics

- Retrieval match score: expected terms found in retrieved evidence titles.
- Groundedness pass rate: answer includes at least one citation.
- Latency: measured in the query response.
- Failure list: cases that need better data, prompts, or retrieval.

## Golden Cases

1. Queue backlog after deploy.
2. Database connection pool exhaustion.

These are synthetic cases built from common public operational patterns.

