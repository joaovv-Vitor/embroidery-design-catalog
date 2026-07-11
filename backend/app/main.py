from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.router import api_router
from app.core.config import get_settings
from app.core.openapi import configure_binary_file_fields
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router)
configure_binary_file_fields(app)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
