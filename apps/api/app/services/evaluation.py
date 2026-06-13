from statistics import mean
from typing import TypedDict

from app.repositories.evaluations import EvaluationRunRepository
from app.schemas.debug import EvaluationRunResponse, QueryRequest
from app.services.evaluation_thresholds import DEFAULT_EVALUATION_THRESHOLDS
from app.services.rag import assistant
from app.services.retrieval import DatabaseRetriever, get_retriever


class GoldenCase(TypedDict):
    question: str
    expected_terms: set[str]
    scenario: str


GOLDEN_CASES: list[GoldenCase] = [
    {
        "scenario": "queue",
        "question": "API latency is high and Redis queue depth keeps growing after a deploy.",
        "expected_terms": {"queue", "worker", "redis"},
    },
    {
        "scenario": "database",
        "question": "Requests fail with connection pool timeout and too many database clients.",
        "expected_terms": {"database", "connection", "pool"},
    },
    {
        "scenario": "latency",
        "question": "The API is slow after deploy and request latency keeps climbing.",
        "expected_terms": {"latency", "worker", "queue"},
    },
    {
        "scenario": "weak_evidence",
        "question": "Something feels wrong but I only have a vague slowdown report.",
        "expected_terms": {"evidence", "incident", "logs"},
    },
    {
        "scenario": "no_evidence",
        "question": "I have no logs, no metrics, and no runbook context yet.",
        "expected_terms": {"evidence", "logs", "incident"},
    },
]


def run_evaluation() -> EvaluationRunResponse:
    scores: list[float] = []
    latencies: list[int] = []
    failures: list[str] = []
    grounded_passes = 0
    citation_passes = 0
    weak_evidence_warnings = 0
    no_evidence_warnings = 0
    weak_evidence_cases = sum(1 for case in GOLDEN_CASES if case["scenario"] == "weak_evidence")
    no_evidence_cases = sum(1 for case in GOLDEN_CASES if case["scenario"] == "no_evidence")
    for case in GOLDEN_CASES:
        response = assistant.answer(QueryRequest(question=case["question"]))
        evidence_surface = " ".join(
            [
                *(citation.title.lower() for citation in response.citations),
                *(citation.snippet.lower() for citation in response.citations),
                *(warning.lower() for warning in response.warnings),
                *(step.lower() for step in response.next_steps),
            ]
        )
        matched = sum(1 for term in case["expected_terms"] if term in evidence_surface)
        score = matched / len(case["expected_terms"])
        scores.append(score)
        latencies.append(response.latency_ms)
        if response.citations:
            grounded_passes += 1
            citation_passes += 1
        has_weak_warning = any("weak" in warning.lower() for warning in response.warnings)
        has_no_evidence_warning = any(
            "no evidence" in warning.lower() for warning in response.warnings
        )
        if case["scenario"] == "weak_evidence" and has_weak_warning:
            weak_evidence_warnings += 1
        if case["scenario"] == "no_evidence" and has_no_evidence_warning:
            no_evidence_warnings += 1
        if score < DEFAULT_EVALUATION_THRESHOLDS.min_mean_retrieval_score:
            failures.append(f"Low retrieval match for: {case['question']}")

    groundedness_pass_rate = round(grounded_passes / len(GOLDEN_CASES), 2)
    citation_presence_rate = round(citation_passes / len(GOLDEN_CASES), 2)
    mean_retrieval_score = round(sum(scores) / len(scores), 2)
    mean_latency_ms = round(mean(latencies), 2)
    weak_evidence_warning_rate = round(weak_evidence_warnings / weak_evidence_cases, 2)
    no_evidence_warning_rate = round(no_evidence_warnings / no_evidence_cases, 2)
    thresholds = {
        "min_mean_retrieval_score": DEFAULT_EVALUATION_THRESHOLDS.min_mean_retrieval_score,
        "min_groundedness_pass_rate": DEFAULT_EVALUATION_THRESHOLDS.min_groundedness_pass_rate,
        "min_citation_presence_rate": DEFAULT_EVALUATION_THRESHOLDS.min_citation_presence_rate,
        "max_mean_latency_ms": DEFAULT_EVALUATION_THRESHOLDS.max_mean_latency_ms,
        "min_weak_evidence_warning_rate": (
            DEFAULT_EVALUATION_THRESHOLDS.min_weak_evidence_warning_rate
        ),
        "min_no_evidence_warning_rate": DEFAULT_EVALUATION_THRESHOLDS.min_no_evidence_warning_rate,
    }

    if groundedness_pass_rate < DEFAULT_EVALUATION_THRESHOLDS.min_groundedness_pass_rate:
        failures.append(
            "Groundedness pass rate fell below "
            f"{DEFAULT_EVALUATION_THRESHOLDS.min_groundedness_pass_rate:.2f}."
        )
    if citation_presence_rate < DEFAULT_EVALUATION_THRESHOLDS.min_citation_presence_rate:
        failures.append(
            "Citation presence rate fell below "
            f"{DEFAULT_EVALUATION_THRESHOLDS.min_citation_presence_rate:.2f}."
        )
    if mean_latency_ms > DEFAULT_EVALUATION_THRESHOLDS.max_mean_latency_ms:
        failures.append(
            "Mean latency exceeded "
            f"{DEFAULT_EVALUATION_THRESHOLDS.max_mean_latency_ms}ms."
        )
    if (
        weak_evidence_warning_rate
        < DEFAULT_EVALUATION_THRESHOLDS.min_weak_evidence_warning_rate
    ):
        failures.append(
            "Weak-evidence warning rate fell below "
            f"{DEFAULT_EVALUATION_THRESHOLDS.min_weak_evidence_warning_rate:.2f}."
        )
    if (
        no_evidence_warning_rate
        < DEFAULT_EVALUATION_THRESHOLDS.min_no_evidence_warning_rate
    ):
        failures.append(
            "No-evidence warning rate fell below "
            f"{DEFAULT_EVALUATION_THRESHOLDS.min_no_evidence_warning_rate:.2f}."
        )

    evaluation_response = EvaluationRunResponse(
        cases_evaluated=len(GOLDEN_CASES),
        mean_retrieval_score=mean_retrieval_score,
        groundedness_pass_rate=groundedness_pass_rate,
        citation_presence_rate=citation_presence_rate,
        mean_latency_ms=mean_latency_ms,
        weak_evidence_warning_rate=weak_evidence_warning_rate,
        no_evidence_warning_rate=no_evidence_warning_rate,
        failures=failures,
        passed=not failures,
        thresholds=thresholds,
    )
    retriever = get_retriever()
    if isinstance(retriever, DatabaseRetriever):
        EvaluationRunRepository(retriever.session).add(
            suite_name="golden_local_v1",
            cases_evaluated=evaluation_response.cases_evaluated,
            mean_retrieval_score=evaluation_response.mean_retrieval_score,
            groundedness_pass_rate=evaluation_response.groundedness_pass_rate,
            citation_presence_rate=evaluation_response.citation_presence_rate,
            mean_latency_ms=evaluation_response.mean_latency_ms,
            weak_evidence_warning_rate=evaluation_response.weak_evidence_warning_rate,
            no_evidence_warning_rate=evaluation_response.no_evidence_warning_rate,
            passed=evaluation_response.passed,
            thresholds=evaluation_response.thresholds,
            failures=evaluation_response.failures,
        )
        retriever.session.commit()
    return evaluation_response

