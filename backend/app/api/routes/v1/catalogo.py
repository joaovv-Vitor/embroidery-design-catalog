from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.db.session import DbSession
from app.models import Categoria, Desenho
from app.schemas.desenho import CatalogoDesenhosResponse, CategoriaDetalheResponse, DesenhoCardResponse

router = APIRouter(prefix="/catalogo", tags=["catálogo"])


def _categoria_detalhe(desenho: Desenho) -> CategoriaDetalheResponse | None:
    if desenho.categoria is None:
        return None
    return CategoriaDetalheResponse(
        id=desenho.categoria.id,
        nome=desenho.categoria.nome,
        cor=desenho.categoria.cor,
        icone=desenho.categoria.icone,
    )


def _card_desenho(desenho: Desenho) -> DesenhoCardResponse:
    return DesenhoCardResponse(
        id=desenho.id,
        nome=desenho.nome,
        favorito=desenho.favorito,
        categoria=_categoria_detalhe(desenho),
        preview_url=f"/api/v1/desenhos/{desenho.id}/preview" if desenho.imagem_preview_chave else None,
    )


def _filtro_busca(termo: str):
    termo_like = f"%{termo}%"
    return or_(Desenho.nome.ilike(termo_like), Categoria.nome.ilike(termo_like))


@router.get("/desenhos")
async def pesquisar_desenhos(
    session: DbSession,
    busca: Annotated[
        str | None,
        Query(max_length=120, description="Pesquisa pelo nome do desenho ou da categoria."),
    ] = None,
    favorito: Annotated[
        bool | None,
        Query(description="Filtra desenhos pelo estado de favorito."),
    ] = None,
    pagina: Annotated[int, Query(ge=1, description="Página de resultados.")] = 1,
    por_pagina: Annotated[int, Query(ge=1, le=100, description="Quantidade de cards por página.")] = 24,
) -> CatalogoDesenhosResponse:
    filtros = [Desenho.excluido_em.is_(None)]
    termo = busca.strip() if busca else None
    if termo:
        filtros.append(_filtro_busca(termo))
    if favorito is not None:
        filtros.append(Desenho.favorito.is_(favorito))

    total_query = select(func.count(Desenho.id)).outerjoin(Desenho.categoria).where(*filtros)
    total = (await session.scalar(total_query)) or 0
    query = (
        select(Desenho)
        .outerjoin(Desenho.categoria)
        .options(selectinload(Desenho.categoria))
        .where(*filtros)
        .order_by(Desenho.nome, Desenho.id)
        .offset((pagina - 1) * por_pagina)
        .limit(por_pagina)
    )
    desenhos = (await session.execute(query)).scalars().all()
    return CatalogoDesenhosResponse(
        itens=[_card_desenho(desenho) for desenho in desenhos],
        total=total,
        pagina=pagina,
        por_pagina=por_pagina,
    )
