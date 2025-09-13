from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from .routes.health import router as health_router
from .routes.index import router as index_router
from .routes.search import router as search_router
from .routes.warmup import router as warmup_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Low-Latency Search API",
        version="0.1.0",
        default_response_class=ORJSONResponse,  # high-performance JSON
    )
    app.include_router(health_router)
    app.include_router(index_router, prefix="/v1")
    app.include_router(search_router, prefix="/v1")
    app.include_router(warmup_router, prefix="/v1")
    return app


app = create_app()
