from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.runtime import build_runtime
from app.services.retrieval import set_retriever


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    runtime = build_runtime()
    set_retriever(runtime.retriever)
    app.state.runtime = runtime
    try:
        yield
    finally:
        runtime.session.close()
        runtime.engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Grounded AI assistant for public and synthetic enterprise debugging cases.",
        lifespan=lifespan,
    )
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()

