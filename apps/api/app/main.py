import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response

from app.api.routes import router
from app.core.config import settings
from app.core.logging import bind_log_context, configure_logging, get_logger, reset_log_context
from app.core.metrics import metrics_registry
from app.core.runtime import build_runtime

configure_logging(settings.log_level)
logger = get_logger(__name__, component="api")
REQUEST_ID_HEADER = "X-Request-ID"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    runtime = build_runtime()
    app.state.runtime = runtime
    logger.info(
        "runtime.started",
        app_env=settings.app_env,
        backend=runtime.backend_name,
        sqlite_fallback=runtime.backend_name == "sqlite_fallback",
    )
    try:
        yield
    finally:
        logger.info("runtime.stopped", backend=runtime.backend_name)
        runtime.engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Grounded AI assistant for public and synthetic enterprise debugging cases.",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def request_context_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
        request.state.request_id = request_id
        reset_log_context()
        bind_log_context(request_id=request_id)
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            logger.exception(
                "http.request.failed",
                method=request.method,
                path=request.url.path,
            )
            raise
        finally:
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            metrics_registry.record_http_request(
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                latency_ms=latency_ms,
            )
            logger.info(
                "http.request.completed",
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                latency_ms=latency_ms,
            )
            reset_log_context()
        response.headers[REQUEST_ID_HEADER] = request_id
        return response

    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()

