from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import EvaluationRunRow


class EvaluationRunRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(
        self,
        suite_name: str,
        cases_evaluated: int,
        mean_retrieval_score: float,
        groundedness_pass_rate: float,
        citation_presence_rate: float,
        mean_latency_ms: float,
        weak_evidence_case_warning_rate: float,
        no_evidence_case_warning_rate: float,
        passed: bool,
        thresholds: dict[str, float | int],
        failures: list[str],
    ) -> None:
        self.session.add(
            EvaluationRunRow(
                suite_name=suite_name,
                cases_evaluated=cases_evaluated,
                mean_retrieval_score=mean_retrieval_score,
                groundedness_pass_rate=groundedness_pass_rate,
                citation_presence_rate=citation_presence_rate,
                mean_latency_ms=mean_latency_ms,
                weak_evidence_case_warning_rate=weak_evidence_case_warning_rate,
                no_evidence_case_warning_rate=no_evidence_case_warning_rate,
                passed=passed,
                thresholds=thresholds,
                failures=failures,
            )
        )
        self.session.flush()

    def count(self) -> int:
        return len(self.session.scalars(select(EvaluationRunRow.id)).all())

    def latest(self) -> EvaluationRunRow | None:
        return self.session.scalar(
            select(EvaluationRunRow).order_by(EvaluationRunRow.created_at.desc())
        )
