from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/desenhos", tags=["desenhos"])


@router.get("")
async def listar_desenhos() -> list[dict[str, str]]:
    return []


@router.get("/{desenho_id}")
async def obter_desenho(desenho_id: int) -> dict[str, int]:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint ainda não implementado.")


@router.patch("/{desenho_id}")
async def atualizar_desenho(desenho_id: int) -> dict[str, int]:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint ainda não implementado.")


@router.patch("/{desenho_id}/favorito")
async def atualizar_favorito(desenho_id: int) -> dict[str, int]:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint ainda não implementado.")


@router.delete("/{desenho_id}")
async def remover_desenho(desenho_id: int) -> dict[str, int]:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint ainda não implementado.")
