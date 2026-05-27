# Evaluation Plan

Evaluation starts deterministic and local. It becomes a CI quality gate in Phase 4.

## Metrics

- Retrieval match score: expected terms found in retrieved evidence titles.
- Groundedness pass rate: answer includes at least one citation.
- Latency: measured in the query response.
- Failure list: cases that need better data, prompts, or retrieval.

## Current Thresholds

The current evaluation is informational only. It should not be treated as a production quality gate yet.

Phase 4 must define pass/fail thresholds for:

- retrieval match score
- groundedness pass rate
- citation presence
- latency
- weak-evidence warning behavior

## Golden Cases

1. Queue backlog after deploy.
2. Database connection pool exhaustion.

These are synthetic cases built from common public operational patterns.

## CI Gate Target

After Phase 4, evaluation should fail CI when retrieval or groundedness quality regresses below documented thresholds.

