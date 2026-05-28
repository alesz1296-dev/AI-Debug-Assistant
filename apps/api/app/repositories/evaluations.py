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
        failures: list[str],
    ) -> None:
        self.session.add(
            EvaluationRunRow(
                suite_name=suite_name,
                cases_evaluated=cases_evaluated,
                mean_retrieval_score=mean_retrieval_score,
                groundedness_pass_rate=groundedness_pass_rate,
                failures=failures,
            )
        )
        self.session.flush()

    def count(self) -> int:
        return len(self.session.scalars(select(EvaluationRunRow.id)).all())
