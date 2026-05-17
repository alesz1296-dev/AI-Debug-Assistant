from app.schemas.debug import EvaluationRunResponse, QueryRequest
from app.services.rag import assistant

GOLDEN_CASES = [
    {
        "question": "API latency is high and Redis queue depth keeps growing after a deploy.",
        "expected_terms": {"queue", "worker", "redis"},
    },
    {
        "question": "Requests fail with connection pool timeout and too many database clients.",
        "expected_terms": {"database", "connection", "pool"},
    },
]


def run_evaluation() -> EvaluationRunResponse:
    scores: list[float] = []
    failures: list[str] = []
    grounded_passes = 0
    for case in GOLDEN_CASES:
        response = assistant.answer(QueryRequest(question=case["question"]))
        retrieved_text = " ".join(citation.title.lower() for citation in response.citations)
        matched = sum(1 for term in case["expected_terms"] if term in retrieved_text)
        score = matched / len(case["expected_terms"])
        scores.append(score)
        if response.citations:
            grounded_passes += 1
        if score < 0.34:
            failures.append(f"Low retrieval match for: {case['question']}")

    return EvaluationRunResponse(
        cases_evaluated=len(GOLDEN_CASES),
        mean_retrieval_score=round(sum(scores) / len(scores), 2),
        groundedness_pass_rate=round(grounded_passes / len(GOLDEN_CASES), 2),
        failures=failures,
    )

