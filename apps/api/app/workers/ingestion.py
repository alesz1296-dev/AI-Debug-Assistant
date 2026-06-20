import sys

from rq import Worker

from app.core.logging import get_logger
from app.services.ingestion_jobs import get_ingestion_queue, get_worker_runtime


def main() -> None:
    burst = "--burst" in sys.argv
    runtime = get_worker_runtime()
    queue = get_ingestion_queue()
    worker = Worker([queue], connection=queue.connection)
    get_logger(__name__, component="worker").info(
        "worker.started",
        queue=queue.name,
        backend=runtime.backend_name,
        burst=burst,
    )
    try:
        worker.work(burst=burst)
    finally:
        get_logger(__name__, component="worker").info(
            "worker.stopped",
            queue=queue.name,
            backend=runtime.backend_name,
            burst=burst,
        )
        runtime.engine.dispose()


if __name__ == "__main__":
    main()
