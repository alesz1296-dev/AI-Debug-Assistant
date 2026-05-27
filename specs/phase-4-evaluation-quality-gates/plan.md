# Phase 4 Plan: Evaluation + Quality Gates

## Approach

Keep deterministic evaluation first. Expand golden cases and promote thresholds into documented gates before introducing external model behavior.

## Metrics

- Retrieval match score.
- Groundedness pass rate.
- Citation presence.
- Latency.
- Weak-evidence warning behavior.

## Validation

- Tests for passing cases.
- Tests for failing cases.
- CI command that can fail when thresholds are not met.
