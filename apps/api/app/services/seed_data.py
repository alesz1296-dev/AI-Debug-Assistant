from app.models.records import KnowledgeRecord

SEED_RECORDS: list[KnowledgeRecord] = [
    KnowledgeRecord(
        collection="incident_cases",
        title="Synthetic queue backlog after deploy",
        source="synthetic://incident/queue-backlog-after-deploy",
        text=(
            "Synthetic incident. After a deploy, API latency increased and background workers "
            "fell behind. Symptoms included Redis queue depth growth, timeout errors, and a "
            "new retry loop. Confirmed cause was a bad worker concurrency setting combined "
            "with unbounded retries. Remediation restored worker concurrency, capped retries, "
            "and added queue-depth alerts."
        ),
        tags=("synthetic", "queue", "redis", "deploy", "latency"),
        metadata={"severity": "high", "confirmed_cause": "bad worker concurrency"},
    ),
    KnowledgeRecord(
        collection="incident_cases",
        title="Synthetic database connection exhaustion",
        source="synthetic://incident/database-connection-exhaustion",
        text=(
            "Synthetic incident. API requests returned intermittent 500 errors while database "
            "CPU stayed moderate. Logs showed connection pool timeout and too many clients. "
            "Confirmed cause was a missing pool limit in a new service path. Remediation set "
            "pool limits, added transaction timeouts, and introduced connection metrics."
        ),
        tags=("synthetic", "postgres", "pool", "timeout"),
        metadata={"severity": "critical", "confirmed_cause": "connection pool exhaustion"},
    ),
    KnowledgeRecord(
        collection="system_logs",
        title="Demo API timeout log",
        source="loghub-style://local-demo/api-timeout",
        text=(
            "2026-01-15T10:04:21Z api ERROR request_id=demo-42 route=/checkout "
            "message='upstream timeout waiting for worker result' latency_ms=30000"
        ),
        tags=("log", "api", "timeout", "worker"),
        metadata={"service": "api", "severity": "ERROR", "synthetic": True},
    ),
    KnowledgeRecord(
        collection="system_logs",
        title="Demo Redis queue depth log",
        source="loghub-style://local-demo/redis-queue-depth",
        text=(
            "2026-01-15T10:05:03Z worker WARN queue=ingestion depth=18420 "
            "message='queue depth above threshold; processing lag increasing'"
        ),
        tags=("log", "redis", "queue", "worker"),
        metadata={"service": "worker", "severity": "WARN", "synthetic": True},
    ),
    KnowledgeRecord(
        collection="knowledge_base",
        title="Runbook: queue backlog triage",
        source="docs/runbooks/queue-backlog.md",
        text=(
            "When queue depth grows, compare enqueue rate, dequeue rate, worker concurrency, "
            "retry rate, and downstream dependency latency. Check recent deploys for changes "
            "to retry behavior, batch size, lock duration, and worker autoscaling."
        ),
        tags=("runbook", "queue", "redis", "workers"),
        metadata={"version": "local-v1"},
    ),
    KnowledgeRecord(
        collection="knowledge_base",
        title="Runbook: database connection pool triage",
        source="docs/runbooks/database-connections.md",
        text=(
            "For connection pool timeouts, inspect active connections, idle transactions, pool "
            "size, request concurrency, transaction duration, and recent code paths that open "
            "sessions. Add limits and timeouts before increasing database capacity."
        ),
        tags=("runbook", "postgres", "pool", "database"),
        metadata={"version": "local-v1"},
    ),
]

