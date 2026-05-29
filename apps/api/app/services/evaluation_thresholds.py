from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvaluationThresholds:
    min_mean_retrieval_score: float = 0.67
    min_groundedness_pass_rate: float = 1.0
    min_citation_presence_rate: float = 1.0
    max_mean_latency_ms: int = 250
    min_weak_evidence_warning_rate: float = 1.0
    min_no_evidence_warning_rate: float = 1.0


DEFAULT_EVALUATION_THRESHOLDS = EvaluationThresholds()
