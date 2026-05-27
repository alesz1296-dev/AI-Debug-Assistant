from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import RetrievalTraceHitRow, RetrievalTraceRow
from app.schemas.debug import CollectionName


class RetrievalTraceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_trace(
        self,
        question: str,
        collections: list[CollectionName],
        top_k: int,
        embedding_provider: str,
        embedding_model: str,
    ) -> UUID:
        trace_id = uuid4()
        self.session.add(
            RetrievalTraceRow(
                id=str(trace_id),
                question=question,
                collections=list(collections),
                top_k=top_k,
                embedding_provider=embedding_provider,
                embedding_model=embedding_model,
            )
        )
        self.session.flush()
        return trace_id

    def add_hit(self, trace_id: UUID, record_id: UUID, rank: int, score: float) -> None:
        self.session.add(
            RetrievalTraceHitRow(
                trace_id=str(trace_id),
                record_id=str(record_id),
                rank=rank,
                score=score,
            )
        )
        self.session.flush()

    def hit_count(self, trace_id: UUID) -> int:
        return len(
            self.session.scalars(
                select(RetrievalTraceHitRow.id).where(
                    RetrievalTraceHitRow.trace_id == str(trace_id)
                )
            ).all()
        )

    def count(self) -> int:
        return len(self.session.scalars(select(RetrievalTraceRow.id)).all())
