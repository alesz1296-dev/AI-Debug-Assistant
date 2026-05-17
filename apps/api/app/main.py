from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Grounded AI assistant for public and synthetic enterprise debugging cases.",
    )
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()

