from fastapi import APIRouter

from app.api.routes.v1.categorias import router as categorias_router
from app.api.routes.v1.desenhos import router as desenhos_router
from app.api.routes.v1.importacoes import router as importacoes_router
from app.api.routes.v1.matrizes import router as matrizes_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(categorias_router)
api_router.include_router(desenhos_router)
api_router.include_router(importacoes_router)
api_router.include_router(matrizes_router)
