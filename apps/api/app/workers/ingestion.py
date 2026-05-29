from rq import Worker

from app.core.logging import get_logger
from app.services.ingestion_jobs import get_ingestion_queue, get_worker_runtime


def main() -> None:
    runtime = get_worker_runtime()
    queue = get_ingestion_queue()
    worker = Worker([queue], connection=queue.connection)
    get_logger(__name__, component="worker").info(
        "worker.started", queue=queue.name, backend=runtime.backend_name
    )
    try:
        worker.work()
    finally:
        get_logger(__name__, component="worker").info(
            "worker.stopped", queue=queue.name, backend=runtime.backend_name
        )
        runtime.session.close()
        runtime.engine.dispose()


if __name__ == "__main__":
    main()
