from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db.models import KnowledgeRecordRow, RecordEmbeddingRow
from app.models.records import KnowledgeRecord
from app.repositories.embeddings import RecordEmbeddingRepository
from app.repositories.records import KnowledgeRecordRepository, row_to_record
from app.repositories.retrieval_traces import RetrievalTraceRepository
from app.schemas.debug import Citation, CollectionName
from app.services.embeddings import LocalEmbeddingModel, cosine_similarity
from app.services.seed_data import SEED_RECORDS


@dataclass(frozen=True)
class RetrievalHit:
    record: KnowledgeRecord
    score: float


@dataclass(frozen=True)
class RetrievalTrace:
    id: UUID
    question: str
    hits: list[RetrievalHit]


class InMemoryRetriever:
    def __init__(self, embedding_model: LocalEmbeddingModel | None = None) -> None:
        self.embedding_model = embedding_model or LocalEmbeddingModel()
        self._records: list[KnowledgeRecord] = []
        self._vectors: dict[UUID, list[float]] = {}
        for record in SEED_RECORDS:
            self.add(record)

    def add(self, record: KnowledgeRecord) -> KnowledgeRecord:
        self._records.append(record)
        self._vectors[record.id] = self.embedding_model.embed(record.text)
        return record

    def search(
        self,
        question: str,
        collections: list[CollectionName],
        top_k: int,
    ) -> RetrievalTrace:
        query_vector = self.embedding_model.embed(question)
        hits = [
            RetrievalHit(
                record=record,
                score=cosine_similarity(query_vector, self._vectors[record.id]),
            )
            for record in self._records
            if record.collection in collections
        ]
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return RetrievalTrace(id=uuid4(), question=question, hits=hits[:top_k])

    def citations_for(self, hits: list[RetrievalHit]) -> list[Citation]:
        return citations_for(hits)


class DatabaseRetriever:
    def __init__(
        self,
        session: Session,
        embedding_model: LocalEmbeddingModel | None = None,
    ) -> None:
        self.session = session
        self.embedding_model = embedding_model or LocalEmbeddingModel()
        self.records = KnowledgeRecordRepository(session)
        self.embeddings = RecordEmbeddingRepository(session)
        self.traces = RetrievalTraceRepository(session)

    def add(self, record: KnowledgeRecord) -> KnowledgeRecord:
        saved_record = self.records.upsert_by_source(record)
        self.embeddings.upsert(
            record_id=saved_record.id,
            vector=self.embedding_model.embed(saved_record.text),
            provider=self.embedding_model.provider,
            model=self.embedding_model.model,
        )
        self.session.commit()
        return saved_record

    def search(
        self,
        question: str,
        collections: list[CollectionName],
        top_k: int,
    ) -> RetrievalTrace:
        query_vector = self.embedding_model.embed(question)
        hits = (
            self._search_postgres(question, collections, top_k, query_vector)
            if self.session.bind is not None and self.session.bind.dialect.name == "postgresql"
            else self._search_portable(question, collections, top_k, query_vector)
        )
        trace_id = self.traces.create_trace(
            question=question,
            collections=collections,
            top_k=top_k,
            embedding_provider=self.embedding_model.provider,
            embedding_model=self.embedding_model.model,
        )
        for rank, hit in enumerate(hits, start=1):
            self.traces.add_hit(trace_id, hit.record.id, rank=rank, score=hit.score)
        self.session.commit()
        return RetrievalTrace(id=trace_id, question=question, hits=hits)

    def citations_for(self, hits: list[RetrievalHit]) -> list[Citation]:
        return citations_for(hits)

    def _search_portable(
        self,
        question: str,
        collections: list[CollectionName],
        top_k: int,
        query_vector: list[float],
    ) -> list[RetrievalHit]:
        rows = self.session.execute(
            select(KnowledgeRecordRow, RecordEmbeddingRow)
            .join(RecordEmbeddingRow, RecordEmbeddingRow.record_id == KnowledgeRecordRow.id)
            .where(KnowledgeRecordRow.collection.in_(collections))
            .where(RecordEmbeddingRow.provider == self.embedding_model.provider)
            .where(RecordEmbeddingRow.model == self.embedding_model.model)
        ).all()
        hits = [
            RetrievalHit(
                record=row_to_record(record_row),
                score=cosine_similarity(query_vector, list(embedding_row.vector)),
            )
            for record_row, embedding_row in rows
        ]
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return hits[:top_k]

    def _search_postgres(
        self,
        question: str,
        collections: list[CollectionName],
        top_k: int,
        query_vector: list[float],
    ) -> list[RetrievalHit]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    kr.id,
                    kr.collection,
                    kr.title,
                    kr.source,
                    kr.text,
                    kr.tags,
                    kr.metadata,
                    1 - (re.vector::text::vector <=> CAST(:query_vector AS vector)) AS score
                FROM knowledge_records kr
                JOIN record_embeddings re ON re.record_id = kr.id
                WHERE kr.collection = ANY(:collections)
                  AND re.provider = :provider
                  AND re.model = :model
                ORDER BY re.vector::text::vector <=> CAST(:query_vector AS vector)
                LIMIT :top_k
                """
            ),
            {
                "collections": collections,
                "provider": self.embedding_model.provider,
                "model": self.embedding_model.model,
                "query_vector": _vector_literal(query_vector),
                "top_k": top_k,
            },
        ).mappings()
        return [
            RetrievalHit(
                record=KnowledgeRecord(
                    id=UUID(str(row["id"])),
                    collection=row["collection"],
                    title=row["title"],
                    source=row["source"],
                    text=row["text"],
                    tags=tuple(row["tags"]),
                    metadata=dict(row["metadata"]),
                ),
                score=float(row["score"]),
            )
            for row in rows
        ]


def citations_for(hits: list[RetrievalHit]) -> list[Citation]:
    return [
        Citation(
            collection=hit.record.collection,
            source=hit.record.source,
            title=hit.record.title,
            snippet=_snippet(hit.record.text),
            score=round(hit.score, 4),
        )
        for hit in hits
    ]


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(value) for value in vector) + "]"


def _snippet(text: str, max_chars: int = 240) -> str:
    clean = " ".join(text.split())
    if len(clean) <= max_chars:
        return clean
    return f"{clean[: max_chars - 3]}..."


_ACTIVE_RETRIEVER: InMemoryRetriever | DatabaseRetriever = InMemoryRetriever()


def get_retriever() -> InMemoryRetriever | DatabaseRetriever:
    return _ACTIVE_RETRIEVER


def set_retriever(new_retriever: InMemoryRetriever | DatabaseRetriever) -> None:
    global _ACTIVE_RETRIEVER
    _ACTIVE_RETRIEVER = new_retriever

