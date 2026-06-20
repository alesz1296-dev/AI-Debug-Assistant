from app.db.init_db import initialize_database
from app.db.types import vector_literal
from app.repositories.retrieval_traces import RetrievalTraceRepository
from app.services.retrieval import DatabaseRetriever
from app.services.seed_records import seed_knowledge_records
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def _session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    initialize_database(engine)
    return Session(engine)


def test_database_retriever_searches_persisted_embeddings() -> None:
    session = _session()
    seed_knowledge_records(session)
    retriever = DatabaseRetriever(session)

    trace = retriever.search(
        question="The Redis queue is growing after a deploy.",
        collections=["incident_cases", "system_logs", "knowledge_base"],
        top_k=3,
    )

    assert trace.hits
    assert trace.hits[0].score >= trace.hits[-1].score
    assert any("queue" in hit.record.title.lower() for hit in trace.hits)


def test_database_retriever_persists_trace_hits() -> None:
    session = _session()
    seed_knowledge_records(session)
    retriever = DatabaseRetriever(session)
    trace_repository = RetrievalTraceRepository(session)

    trace = retriever.search(
        question="Requests fail with database connection pool timeout.",
        collections=["incident_cases", "knowledge_base"],
        top_k=2,
    )

    assert trace_repository.count() == 1
    assert trace_repository.hit_count(trace.id) == len(trace.hits)


def test_vector_literal_matches_pgvector_input_format() -> None:
    assert vector_literal([0.1, -0.2, 0.0]) == "[0.1,-0.2,0.0]"
