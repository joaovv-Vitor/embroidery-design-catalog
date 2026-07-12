from datetime import datetime, timedelta, timezone
from typing import Annotated

from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException, Path, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.session import DbSession
from app.models import Categoria, Desenho, Matriz
from app.schemas.desenho import (
    AtualizarDesenhoRequest,
    AtualizarFavoritoRequest,
    CategoriaDetalheResponse,
    DesenhoDetalheResponse,
    DesenhoResumoResponse,
    MatrizVariacaoResponse,
)
from app.schemas.lixeira import ConfirmarRemocaoRequest, DesenhoLixeiraResponse
from app.services.remocao_desenho import RemocaoDesenhoService
from app.services.storage import ObjectStorage

router = APIRouter(prefix="/desenhos", tags=["desenhos"])


def _recuperavel_ate(excluido_em: datetime) -> datetime:
    return excluido_em + timedelta(days=get_settings().trash_retention_days)


def _resumo_desenho(desenho: Desenho) -> DesenhoResumoResponse:
    return DesenhoResumoResponse(
        id=desenho.id,
        nome=desenho.nome,
        categoria_id=desenho.categoria_id,
        favorito=desenho.favorito,
    )


def _lixeira_desenho(desenho: Desenho) -> DesenhoLixeiraResponse:
    return DesenhoLixeiraResponse(
        id=desenho.id,
        nome=desenho.nome,
        preview_url=f"/api/v1/desenhos/lixeira/{desenho.id}/preview" if desenho.imagem_preview_chave else None,
        excluido_em=desenho.excluido_em,
        recuperavel_ate=_recuperavel_ate(desenho.excluido_em),
        aviso="A remoção não altera cópias físicas em pendrives ou computadores.",
    )


def _categoria_detalhe(desenho: Desenho) -> CategoriaDetalheResponse | None:
    if desenho.categoria is None:
        return None
    return CategoriaDetalheResponse(
        id=desenho.categoria.id,
        nome=desenho.categoria.nome,
        cor=desenho.categoria.cor,
        icone=desenho.categoria.icone,
    )


def _detalhe_desenho(desenho: Desenho) -> DesenhoDetalheResponse:
    matrizes = [
        MatrizVariacaoResponse(
            id=matriz.id,
            formato=matriz.formato,
            rotulo_tamanho=matriz.rotulo_tamanho,
            largura_mm=float(matriz.largura_mm),
            altura_mm=float(matriz.altura_mm),
            quantidade_cores=matriz.quantidade_cores,
            quantidade_pontos=matriz.quantidade_pontos,
            origem_identificacao=matriz.origem_importacao.identificacao if matriz.origem_importacao else None,
            caminho_relativo_origem=matriz.caminho_relativo_origem,
            download_url=f"/api/v1/matrizes/{matriz.id}/download",
        )
        for matriz in sorted(desenho.matrizes, key=lambda matriz: matriz.id)
    ]
    return DesenhoDetalheResponse(
        **_resumo_desenho(desenho).model_dump(),
        descricao=desenho.descricao,
        categoria=_categoria_detalhe(desenho),
        preview_url=f"/api/v1/desenhos/{desenho.id}/preview" if desenho.imagem_preview_chave else None,
        matrizes=matrizes,
    )


def _storage_http_exception(error: ClientError) -> HTTPException:
    error_code = error.response.get("Error", {}).get("Code")
    if error_code in {"404", "NoSuchKey", "NotFound"}:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado no armazenamento.")
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Não foi possível acessar o armazenamento.")


async def _obter_desenho_ativo(desenho_id: int, session: DbSession) -> Desenho:
    query = select(Desenho).where(Desenho.id == desenho_id, Desenho.excluido_em.is_(None))
    desenho = await session.scalar(query)
    if desenho is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Desenho não encontrado.")
    return desenho


@router.get("/lixeira")
async def listar_lixeira(session: DbSession) -> list[DesenhoLixeiraResponse]:
    query = select(Desenho).where(Desenho.excluido_em.is_not(None)).order_by(Desenho.excluido_em.desc())
    desenhos = (await session.execute(query)).scalars().all()
    return [_lixeira_desenho(desenho) for desenho in desenhos]


@router.get("/lixeira/{desenho_id}/preview")
async def visualizar_preview_lixeira(
    desenho_id: Annotated[int, Path(ge=1)],
    session: DbSession,
) -> StreamingResponse:
    desenho = await session.scalar(
        select(Desenho).where(Desenho.id == desenho_id, Desenho.excluido_em.is_not(None))
    )
    if desenho is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Desenho na lixeira não encontrado.")
    if desenho.imagem_preview_chave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preview não disponível para este desenho.")

    try:
        content_type, content = await ObjectStorage().open_object_stream(desenho.imagem_preview_chave)
    except ClientError as error:
        raise _storage_http_exception(error) from error

    return StreamingResponse(content, media_type=content_type or "image/png")


@router.get("/{desenho_id}/preview")
async def visualizar_preview(
    desenho_id: Annotated[int, Path(ge=1)],
    session: DbSession,
) -> StreamingResponse:
    desenho = await _obter_desenho_ativo(desenho_id, session)
    if desenho.imagem_preview_chave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preview não disponível para este desenho.")

    try:
        content_type, content = await ObjectStorage().open_object_stream(desenho.imagem_preview_chave)
    except ClientError as error:
        raise _storage_http_exception(error) from error

    return StreamingResponse(content, media_type=content_type or "image/png")


@router.get("/{desenho_id}")
async def obter_desenho(
    desenho_id: Annotated[int, Path(ge=1)],
    session: DbSession,
) -> DesenhoDetalheResponse:
    query = (
        select(Desenho)
        .options(
            selectinload(Desenho.categoria),
            selectinload(Desenho.matrizes).selectinload(Matriz.origem_importacao),
        )
        .where(Desenho.id == desenho_id, Desenho.excluido_em.is_(None))
    )
    desenho = await session.scalar(query)
    if desenho is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Desenho não encontrado.")
    return _detalhe_desenho(desenho)


@router.patch("/{desenho_id}")
async def atualizar_desenho(
    desenho_id: Annotated[int, Path(ge=1)],
    dados: AtualizarDesenhoRequest,
    session: DbSession,
) -> DesenhoResumoResponse:
    desenho = await _obter_desenho_ativo(desenho_id, session)

    valores = dados.model_dump(exclude_unset=True)
    if "nome" in valores:
        desenho.nome = valores["nome"]
    if "categoria_id" in valores:
        categoria_id = valores["categoria_id"]
        if categoria_id is not None and await session.get(Categoria, categoria_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
        desenho.categoria_id = valores["categoria_id"]

    await session.commit()
    return _resumo_desenho(desenho)


@router.patch("/{desenho_id}/favorito")
async def atualizar_favorito(
    desenho_id: Annotated[int, Path(ge=1)],
    dados: AtualizarFavoritoRequest,
    session: DbSession,
) -> DesenhoResumoResponse:
    desenho = await _obter_desenho_ativo(desenho_id, session)

    desenho.favorito = dados.favorito
    await session.commit()
    return _resumo_desenho(desenho)


@router.delete("/{desenho_id}")
async def mover_desenho_para_lixeira(
    desenho_id: Annotated[int, Path(ge=1)],
    dados: ConfirmarRemocaoRequest,
    session: DbSession,
) -> DesenhoLixeiraResponse:
    desenho = await _obter_desenho_ativo(desenho_id, session)
    desenho.excluido_em = datetime.now(timezone.utc)
    await session.commit()

    return _lixeira_desenho(desenho)


@router.post("/{desenho_id}/restaurar")
async def restaurar_desenho(
    desenho_id: Annotated[int, Path(ge=1)],
    session: DbSession,
) -> DesenhoResumoResponse:
    desenho = await session.scalar(select(Desenho).where(Desenho.id == desenho_id, Desenho.excluido_em.is_not(None)))
    if desenho is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Desenho na lixeira não encontrado.")
    if datetime.now(timezone.utc) > _recuperavel_ate(desenho.excluido_em):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="O prazo para recuperar este desenho expirou.")

    desenho.excluido_em = None
    await session.commit()
    return _resumo_desenho(desenho)


@router.delete("/{desenho_id}/permanente", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_desenho_permanentemente(
    desenho_id: Annotated[int, Path(ge=1)],
    dados: ConfirmarRemocaoRequest,
    session: DbSession,
) -> None:
    query = (
        select(Desenho)
        .options(selectinload(Desenho.matrizes).selectinload(Matriz.arquivo_backup))
        .where(Desenho.id == desenho_id, Desenho.excluido_em.is_not(None))
    )
    desenho = await session.scalar(query)
    if desenho is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Desenho na lixeira não encontrado.")

    await RemocaoDesenhoService().excluir_permanentemente(session, desenho)
