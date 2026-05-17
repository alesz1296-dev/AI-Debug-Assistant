from dataclasses import dataclass
from uuid import UUID, uuid4

from app.models.records import KnowledgeRecord
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


def _snippet(text: str, max_chars: int = 240) -> str:
    clean = " ".join(text.split())
    if len(clean) <= max_chars:
        return clean
    return f"{clean[: max_chars - 3]}..."


retriever = InMemoryRetriever()

