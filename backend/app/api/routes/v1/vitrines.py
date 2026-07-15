import json
from datetime import UTC, datetime
from html import escape
from typing import Annotated

from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException, Path, status
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.session import DbSession
from app.models import ItemVitrine, Vitrine
from app.schemas.vitrine import (
    CriarVitrineRequest,
    CriarVitrineResponse,
    ItemVitrinePublicaResponse,
    ItemVitrineResponse,
    VitrinePublicaResponse,
    VitrineResponse,
)
from app.services.storage import ObjectStorage
from app.services.vitrine import DesenhosVitrineNaoEncontradosError, VitrineService

router = APIRouter(prefix="/vitrines", tags=["vitrines"])


def _item_response(token: str, item: ItemVitrine) -> ItemVitrineResponse:
    return ItemVitrineResponse(
        id=item.id,
        desenho_id=item.desenho_id,
        nome=item.nome_snapshot,
        preview_url=(
            f"/api/v1/vitrines/{token}/itens/{item.token}/preview" if item.preview_chave_snapshot else None
        ),
    )


def _vitrine_publica_response(vitrine: Vitrine) -> VitrinePublicaResponse:
    itens = [
        ItemVitrinePublicaResponse(
            numero=numero,
            nome=item.nome_snapshot,
            preview_url=(
                f"/api/v1/vitrines/{vitrine.token}/itens/{item.token}/preview"
                if item.preview_chave_snapshot
                else None
            ),
        )
        for numero, item in enumerate(vitrine.itens, start=1)
    ]
    return VitrinePublicaResponse(
        titulo=vitrine.titulo,
        nome_cliente=vitrine.nome_cliente,
        expira_em=vitrine.expira_em,
        quantidade_desenhos=len(itens),
        itens=itens,
    )


def _vitrine_response(vitrine: Vitrine) -> VitrineResponse:
    itens = [_item_response(vitrine.token, item) for item in vitrine.itens]
    return VitrineResponse(
        titulo=vitrine.titulo,
        nome_cliente=vitrine.nome_cliente,
        criado_em=vitrine.criado_em,
        expira_em=vitrine.expira_em,
        quantidade_desenhos=len(itens),
        itens=itens,
    )


async def _obter_vitrine_valida(token: str, session: DbSession) -> Vitrine:
    query = select(Vitrine).options(selectinload(Vitrine.itens)).where(Vitrine.token == token)
    vitrine = await session.scalar(query)
    if vitrine is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vitrine não encontrada.")
    if not vitrine.ativa:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Esta vitrine foi desativada.")
    if vitrine.expira_em <= datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Esta vitrine expirou.")
    return vitrine


@router.post("", status_code=status.HTTP_201_CREATED)
async def criar_vitrine(dados: CriarVitrineRequest, session: DbSession) -> CriarVitrineResponse:
    try:
        vitrine = await VitrineService().criar(session, dados)
    except DesenhosVitrineNaoEncontradosError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"mensagem": str(error), "desenho_ids": error.desenho_ids},
        ) from error
    except ClientError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível preservar uma das previews da vitrine.",
        ) from error

    response = _vitrine_response(vitrine)
    return CriarVitrineResponse(
        **response.model_dump(),
        token=vitrine.token,
        link_publico=(
            f"{get_settings().api_public_url.rstrip('/')}/api/v1/vitrines/{vitrine.token}/compartilhar"
        ),
    )


@router.get("/{token}")
async def obter_vitrine(
    token: Annotated[str, Path(min_length=20, max_length=64)],
    session: DbSession,
) -> VitrinePublicaResponse:
    return _vitrine_publica_response(await _obter_vitrine_valida(token, session))


@router.get("/{token}/compartilhar", response_class=HTMLResponse, include_in_schema=False)
async def compartilhar_vitrine(
    token: Annotated[str, Path(min_length=20, max_length=64)],
    session: DbSession,
) -> HTMLResponse:
    try:
        vitrine = await _obter_vitrine_valida(token, session)
    except HTTPException as error:
        message = escape(str(error.detail))
        return HTMLResponse(
            f"""<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body><main><h1>Vitrine indisponível</h1><p>{message}</p></main></body>
</html>""",
            status_code=error.status_code,
        )
    settings = get_settings()
    frontend_url = f"{settings.frontend_public_url.rstrip('/')}/vitrines/{token}"
    share_url = f"{settings.api_public_url.rstrip('/')}/api/v1/vitrines/{token}/compartilhar"
    preview_item = next((item for item in vitrine.itens if item.preview_chave_snapshot), None)
    preview_url = None
    if preview_item is not None:
        preview_url = (
            f"{settings.api_public_url.rstrip('/')}/api/v1/vitrines/"
            f"{token}/itens/{preview_item.token}/preview"
        )

    title = escape(vitrine.titulo, quote=True)
    client_text = f" para {vitrine.nome_cliente}" if vitrine.nome_cliente else ""
    description = escape(f"Confira as opções de bordado selecionadas{client_text}.", quote=True)
    image_meta = f'<meta property="og:image" content="{escape(preview_url, quote=True)}">' if preview_url else ""
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{escape(share_url, quote=True)}">
  {image_meta}
  <meta name="twitter:card" content="summary_large_image">
  <script>window.location.replace({json.dumps(frontend_url)});</script>
</head>
<body>
  <p>Redirecionando para a vitrine...</p>
  <noscript><a href="{escape(frontend_url, quote=True)}">Abrir vitrine</a></noscript>
</body>
</html>"""
    return HTMLResponse(html)


@router.get("/{token}/itens/{item_token}/preview")
async def visualizar_preview_vitrine(
    token: Annotated[str, Path(min_length=20, max_length=64)],
    item_token: Annotated[str, Path(min_length=20, max_length=64)],
    session: DbSession,
) -> StreamingResponse:
    vitrine = await _obter_vitrine_valida(token, session)
    item = next((item for item in vitrine.itens if item.token == item_token), None)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado nesta vitrine.")
    if item.preview_chave_snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preview não disponível para este item.")

    try:
        content_type, content = await ObjectStorage().open_object_stream(item.preview_chave_snapshot)
    except ClientError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preview da vitrine não encontrada.",
        ) from error
    return StreamingResponse(content, media_type=content_type or "image/png")
