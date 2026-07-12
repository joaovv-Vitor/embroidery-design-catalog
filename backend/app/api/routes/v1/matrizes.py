from typing import Annotated
from urllib.parse import quote

from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException, Path, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.db.session import DbSession
from app.models import Desenho, Matriz, OrigemImportacao
from app.schemas.matriz import AtualizarMatrizRequest, MatrizAtualizadaResponse
from app.services.storage import ObjectStorage

router = APIRouter(tags=["matrizes"])


def _arquivo_backup_indisponivel() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="O arquivo de backup desta matriz não está disponível para download.",
    )


@router.get(
    "/matrizes/{matriz_id}/download",
    summary="Baixar matriz original",
    responses={404: {"description": "Matriz ou arquivo de backup não encontrado."}},
)
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
            raise _arquivo_backup_indisponivel() from error
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
) -> MatrizAtualizadaResponse:
    query = select(Matriz).options(selectinload(Matriz.origem_importacao)).where(Matriz.id == matriz_id)
    matriz = (await session.execute(query)).scalar_one_or_none()
    if matriz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matriz não encontrada.")

    valores = dados.model_dump(exclude_unset=True)
    if "origem_importacao_id" in valores:
        origem_id = valores["origem_importacao_id"]
        if origem_id is not None and await session.get(OrigemImportacao, origem_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Origem não encontrada.")
        matriz.origem_importacao_id = origem_id
    if "identificacao_origem" in valores:
        identificacao = valores["identificacao_origem"]
        if identificacao is None:
            matriz.origem_importacao = None
        elif matriz.origem_importacao is None:
            matriz.origem_importacao = OrigemImportacao(identificacao=identificacao, tipo="manual")
        elif matriz.origem_importacao.identificacao != identificacao:
            total_vinculos = await session.scalar(
                select(func.count(Matriz.id)).where(
                    Matriz.origem_importacao_id == matriz.origem_importacao_id
                )
            )
            if (total_vinculos or 0) > 1:
                matriz.origem_importacao = OrigemImportacao(identificacao=identificacao, tipo="manual")
            else:
                matriz.origem_importacao.identificacao = identificacao
    if "caminho_relativo_origem" in valores:
        matriz.caminho_relativo_origem = valores["caminho_relativo_origem"]

    await session.commit()
    return MatrizAtualizadaResponse(
        id=matriz.id,
        origem_importacao_id=matriz.origem_importacao_id,
        identificacao_origem=matriz.origem_importacao.identificacao if matriz.origem_importacao else None,
        caminho_relativo_origem=matriz.caminho_relativo_origem,
    )
