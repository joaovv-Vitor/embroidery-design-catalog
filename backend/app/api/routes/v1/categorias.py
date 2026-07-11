from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("")
async def listar_categorias() -> list[dict[str, str]]:
    return []


@router.post("")
async def criar_categoria() -> dict[str, str]:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint ainda não implementado.")
