# Evaluation Plan

Evaluation starts deterministic and local. It becomes a CI quality gate in Phase 4.

## Metrics

- Retrieval match score: expected terms found in retrieved evidence titles.
- Groundedness pass rate: answer includes at least one citation.
- Citation presence rate: cases that returned at least one citation.
- Mean latency: measured in the query response.
- Weak-evidence warning rate: weak-evidence cases that triggered the expected warning.
- No-evidence warning rate: no-evidence cases that triggered the expected warning.
- Failure list: cases that need better data, prompts, or retrieval.

## Current Thresholds

Phase 4 defines these initial numeric thresholds:

- minimum mean retrieval score: `0.67`
- minimum groundedness pass rate: `1.00`
- minimum citation presence rate: `1.00`
- maximum mean latency: `250 ms`
- minimum weak-evidence warning rate: `1.00`
- minimum no-evidence warning rate: `1.00`

These thresholds are intentionally strict at the start so the suite stays honest. They are surfaced in the evaluation response and enforced by the evaluation gate.

An evaluation run passes when `passed` is `true`, which means no threshold checks failed. A run fails when `passed` is `false`, and the `failures` list explains why.

The evaluation response now also includes:

- `citation_presence_rate`
- `mean_latency_ms`
- `weak_evidence_warning_rate`
- `no_evidence_warning_rate`
- `thresholds`
- `passed`

When the active retriever is database-backed, evaluation runs are also persisted with the metrics above, the threshold set used for the run, and the final pass/fail result.

## Golden Cases

1. Queue backlog after deploy.
2. Database connection pool exhaustion.
3. Latency increase after deploy.
4. Weak-evidence triage prompt.
5. No-evidence triage prompt.

These are synthetic cases built from common public operational patterns.

## CI Gate Target

Phase 4 is complete. Evaluation should now fail CI when retrieval, grounding, citation presence, latency, or warning behavior regresses below documented thresholds.

The CI command should run the evaluation suite and exit non-zero whenever evaluation reports `passed = false`.

Recommended CI check:

```bash
python -m pytest apps/api/tests -q
```

For the actual quality gate, CI should do all of the following:

1. seed or load the deterministic evaluation corpus
2. run the evaluation entrypoint against the live service or equivalent Python path
3. fail the job if `passed` is `false`
4. fail the job if `failures` is non-empty
5. record the threshold values used for the run so regressions are traceable

The quality gate should be treated as a release blocker, not just a report.

