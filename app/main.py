from fastapi import FastAPI

from .routes.health import router as health_router
from .routes.search import router as search_router


def create_app() -> FastAPI:
    app = FastAPI(title="Low-Latency Search API", version="0.1.0")
    app.include_router(health_router)
    app.include_router(search_router, prefix="/v1")
    return app


app = create_app()
