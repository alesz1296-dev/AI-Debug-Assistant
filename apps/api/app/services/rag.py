import time

from app.schemas.debug import QueryRequest, QueryResponse
from app.services.retrieval import retriever


class GroundedDebugAssistant:
    model_name = "local-grounded-debug-assistant-v1"

    def answer(self, request: QueryRequest) -> QueryResponse:
        started = time.perf_counter()
        trace = retriever.search(request.question, request.collections, request.top_k)
        citations = retriever.citations_for(trace.hits)
        top_titles = [hit.record.title for hit in trace.hits[:3]]
        confidence = _confidence([hit.score for hit in trace.hits])
        warnings = []
        if confidence < 0.35:
            warnings.append(
                "Evidence is weak. Treat this as a triage starting point, not a conclusion."
            )
        if not citations:
            warnings.append(
                "No evidence was retrieved from the indexed public or synthetic corpus."
            )

        hypotheses = _hypotheses_from_hits(top_titles)
        next_steps = _next_steps_from_hits(top_titles)
        answer = _compose_answer(request.question, top_titles, confidence)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return QueryResponse(
            answer=answer,
            hypotheses=hypotheses,
            citations=citations,
            confidence=confidence,
            retrieval_trace_id=trace.id,
            model=self.model_name,
            latency_ms=latency_ms,
            warnings=warnings,
            next_steps=next_steps,
        )


def _confidence(scores: list[float]) -> float:
    if not scores:
        return 0.0
    bounded = max(0.0, min(1.0, sum(max(score, 0.0) for score in scores[:3]) / 3))
    return round(bounded, 2)


def _hypotheses_from_hits(titles: list[str]) -> list[str]:
    joined = " ".join(titles).lower()
    hypotheses = []
    if "queue" in joined or "redis" in joined or "worker" in joined:
        hypotheses.append(
            "Queue processing is lagging because worker throughput dropped or retries spiked."
        )
    if "database" in joined or "connection" in joined or "postgres" in joined:
        hypotheses.append("Database connection pool exhaustion may be causing request failures.")
    if not hypotheses:
        hypotheses.append(
            "The issue needs more evidence before a strong root-cause hypothesis is justified."
        )
    return hypotheses


def _next_steps_from_hits(titles: list[str]) -> list[str]:
    joined = " ".join(titles).lower()
    steps = ["Preserve the incident timeline and collect logs from the affected time window."]
    if "queue" in joined or "redis" in joined or "worker" in joined:
        steps.extend(
            [
                "Compare enqueue rate, dequeue rate, retry rate, and worker concurrency.",
                "Check the most recent deploy for retry, batch-size, or worker scaling changes.",
            ]
        )
    if "database" in joined or "connection" in joined or "postgres" in joined:
        steps.extend(
            [
                "Inspect active database connections, idle transactions, and pool timeout metrics.",
                "Verify new code paths close sessions and enforce transaction timeouts.",
            ]
        )
    return steps


def _compose_answer(question: str, titles: list[str], confidence: float) -> str:
    if not titles:
        return (
            "I do not have enough indexed evidence to answer this safely. Add public logs, "
            "synthetic cases, or runbook material and run the query again."
        )
    evidence = "; ".join(titles)
    return (
        f"Based on the retrieved public/synthetic evidence, the most relevant pattern for "
        f"'{question}' is connected to: {evidence}. Confidence is {confidence:.2f}; use the "
        "citations and next steps to verify before declaring root cause."
    )


assistant = GroundedDebugAssistant()
