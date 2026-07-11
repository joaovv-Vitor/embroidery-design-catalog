from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import select

from app.db.session import DbSession
from app.models import Matriz
from app.schemas.matriz import AtualizarMatrizRequest

router = APIRouter(tags=["matrizes"])


@router.get("/matrizes/{matriz_id}/download")
async def baixar_matriz(matriz_id: Annotated[int, Path(ge=1)]) -> dict[str, int]:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint ainda não implementado.")


@router.patch("/matrizes/{matriz_id}")
async def atualizar_matriz(
    matriz_id: Annotated[int, Path(ge=1)],
    dados: AtualizarMatrizRequest,
    session: DbSession,
) -> dict[str, int | str | None]:
    query = select(Matriz).where(Matriz.id == matriz_id)
    matriz = (await session.execute(query)).scalar_one_or_none()
    if matriz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matriz não encontrada.")

    valores = dados.model_dump(exclude_unset=True)
    if "origem_importacao_id" in valores:
        matriz.origem_importacao_id = valores["origem_importacao_id"]
    if "caminho_relativo_origem" in valores:
        matriz.caminho_relativo_origem = valores["caminho_relativo_origem"]

    await session.commit()
    return {
        "id": matriz.id,
        "origem_importacao_id": matriz.origem_importacao_id,
        "caminho_relativo_origem": matriz.caminho_relativo_origem,
    }
