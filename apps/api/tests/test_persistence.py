from app.db.init_db import initialize_database
from app.models.records import KnowledgeRecord
from app.repositories.embeddings import RecordEmbeddingRepository
from app.repositories.evaluations import EvaluationRunRepository
from app.repositories.records import KnowledgeRecordRepository
from app.repositories.retrieval_traces import RetrievalTraceRepository
from app.services.embeddings import LocalEmbeddingModel
from app.services.evaluation import run_evaluation
from app.services.retrieval import DatabaseRetriever, get_retriever, set_retriever
from app.services.seed_data import SEED_RECORDS
from app.services.seed_records import seed_knowledge_records
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def _session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    initialize_database(engine)
    return Session(engine)


def test_seed_knowledge_records_is_idempotent() -> None:
    session = _session()

    first_count = seed_knowledge_records(session)
    second_count = seed_knowledge_records(session)

    repository = KnowledgeRecordRepository(session)
    embedding_repository = RecordEmbeddingRepository(session)
    assert first_count == len(SEED_RECORDS)
    assert second_count == len(SEED_RECORDS)
    assert repository.count() == len(SEED_RECORDS)
    assert embedding_repository.count() == len(SEED_RECORDS)


def test_record_persists_and_can_be_loaded_by_id() -> None:
    session = _session()
    repository = KnowledgeRecordRepository(session)
    record = KnowledgeRecord(
        collection="knowledge_base",
        title="Runbook: test persistence",
        source="docs/runbooks/test-persistence.md",
        text="This runbook proves records can be stored and loaded from durable state.",
        tags=("runbook", "test"),
        metadata={"synthetic": True},
    )

    saved = repository.upsert_by_source(record)
    session.commit()
    session.expunge_all()

    loaded = repository.get(saved.id)

    assert loaded is not None
    assert loaded.id == saved.id
    assert loaded.source == record.source
    assert loaded.tags == record.tags
    assert loaded.metadata == record.metadata


def test_seed_records_can_be_listed_by_collection() -> None:
    session = _session()
    seed_knowledge_records(session)
    repository = KnowledgeRecordRepository(session)

    records = repository.list_by_collection("incident_cases")

    assert {record.source for record in records} == {
        "synthetic://incident/queue-backlog-after-deploy",
        "synthetic://incident/database-connection-exhaustion",
    }


def test_seed_records_persist_embeddings() -> None:
    session = _session()
    seed_knowledge_records(session)
    record_repository = KnowledgeRecordRepository(session)
    embedding_repository = RecordEmbeddingRepository(session)
    embedding_model = LocalEmbeddingModel()

    records = record_repository.list_by_collection("knowledge_base")
    vector = embedding_repository.get_vector(
        records[0].id,
        embedding_model.provider,
        embedding_model.model,
    )

    assert vector is not None
    assert len(vector) == embedding_model.dimensions


def test_retrieval_trace_and_hits_are_persisted() -> None:
    session = _session()
    seed_knowledge_records(session)
    record_repository = KnowledgeRecordRepository(session)
    trace_repository = RetrievalTraceRepository(session)
    embedding_model = LocalEmbeddingModel()

    records = record_repository.list_by_collection("incident_cases")
    trace_id = trace_repository.create_trace(
        question="Why is the Redis queue growing?",
        collections=["incident_cases"],
        top_k=2,
        embedding_provider=embedding_model.provider,
        embedding_model=embedding_model.model,
    )
    trace_repository.add_hit(trace_id, records[0].id, rank=1, score=0.91)
    trace_repository.add_hit(trace_id, records[1].id, rank=2, score=0.74)
    session.commit()

    assert trace_repository.count() == 1
    assert trace_repository.hit_count(trace_id) == 2


def test_evaluation_runs_are_persisted() -> None:
    session = _session()
    seed_knowledge_records(session)
    original = get_retriever()
    set_retriever(DatabaseRetriever(session))
    try:
        response = run_evaluation()
    finally:
        set_retriever(original)

    repository = EvaluationRunRepository(session)

    assert response.cases_evaluated == 2
    assert response.groundedness_pass_rate > 0
    assert repository.count() == 1
