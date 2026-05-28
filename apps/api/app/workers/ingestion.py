from rq import Worker

from app.services.ingestion_jobs import get_ingestion_queue, get_worker_runtime


def main() -> None:
    runtime = get_worker_runtime()
    queue = get_ingestion_queue()
    worker = Worker([queue], connection=queue.connection)
    try:
        worker.work()
    finally:
        runtime.session.close()
        runtime.engine.dispose()


if __name__ == "__main__":
    main()
