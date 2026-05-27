# Phase 4 Spec: Evaluation + Quality Gates

## Goal

Turn evaluation from a demo endpoint into a quality gate that can protect retrieval and grounded-answer behavior.

## Requirements

- Expand golden cases beyond the current two cases.
- Define pass/fail thresholds for retrieval score, groundedness, citation presence, latency, and weak-evidence warnings.
- Make evaluation suitable for CI regression checks.
- Record failures in a way that helps improve data, retrieval, or answer composition.

## Acceptance Criteria

- Evaluation returns deterministic pass/fail status.
- CI can fail on quality regression.
- Golden cases cover at least queue, database, latency, weak evidence, and no-evidence scenarios.
- Documentation explains how to interpret failures.

## Out Of Scope

- Human evaluation platform.
- LLM-as-judge dependency.
- Dashboard visualization.
