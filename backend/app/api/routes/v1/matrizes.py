from typing import Annotated
from urllib.parse import quote

from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException, Path, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import DbSession
from app.models import Desenho, Matriz
from app.schemas.matriz import AtualizarMatrizRequest
from app.services.storage import ObjectStorage

router = APIRouter(tags=["matrizes"])


@router.get("/matrizes/{matriz_id}/download")
async def baixar_matriz(
    matriz_id: Annotated[int, Path(ge=1)],
    session: DbSession,
) -> StreamingResponse:
    query = (
        select(Matriz)
        .join(Matriz.desenho)
        .options(selectinload(Matriz.arquivo_backup))
        .where(Matriz.id == matriz_id, Desenho.excluido_em.is_(None))
    )
    matriz = await session.scalar(query)
    if matriz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matriz não encontrada.")

    try:
        content_type, content = await ObjectStorage().open_object_stream(matriz.arquivo_backup.chave_storage)
    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code")
        if error_code in {"404", "NoSuchKey", "NotFound"}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arquivo não encontrado no armazenamento.",
            ) from error
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível acessar o armazenamento.",
        ) from error

    nome_arquivo = quote(matriz.arquivo_backup.nome_original)
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{nome_arquivo}"}
    return StreamingResponse(
        content,
        media_type=content_type or matriz.arquivo_backup.mime_type,
        headers=headers,
    )


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
