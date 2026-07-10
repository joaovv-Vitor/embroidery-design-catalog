from fastapi import FastAPI

# from app.api.routes.desenhos import router as desenhos_router
# from app.api.routes.importacoes import router as importacoes_router
# from app.api.routes.matrizes import router as matrizes_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)
# app.include_router(importacoes_router)
# app.include_router(desenhos_router)
# app.include_router(matrizes_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
