from fastapi import APIRouter, HTTPException, status

router = APIRouter(tags=["matrizes"])


@router.get("/matrizes/{matriz_id}/download")
async def baixar_matriz(matriz_id: int) -> dict[str, int]:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint ainda não implementado.")
