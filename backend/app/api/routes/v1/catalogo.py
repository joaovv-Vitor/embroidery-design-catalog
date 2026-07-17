from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.db.session import DbSession
from app.models import Categoria, Desenho
from app.schemas.desenho import (
    CATALOG_DEFAULT_PAGE_SIZE,
    CATALOG_MAX_PAGE_SIZE,
    CatalogoDesenhosResponse,
    CatalogOrderBy,
    CatalogOrderDirection,
    CategoriaDetalheResponse,
    DesenhoCardResponse,
)

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


def _ordenacao_catalogo(
    ordenar_por: CatalogOrderBy,
    ordem: CatalogOrderDirection,
) -> tuple[object, object]:
    campos = {
        CatalogOrderBy.NOME: Desenho.nome,
        CatalogOrderBy.CRIADO_EM: Desenho.criado_em,
        CatalogOrderBy.ATUALIZADO_EM: Desenho.atualizado_em,
    }
    campo = campos[ordenar_por]
    if ordem is CatalogOrderDirection.ASC:
        return campo.asc(), Desenho.id.asc()
    return campo.desc(), Desenho.id.desc()


@router.get("/desenhos")
async def pesquisar_desenhos(
    session: DbSession,
    busca: Annotated[
        str | None,
        Query(max_length=120, description="Pesquisa pelo nome do desenho ou da categoria."),
    ] = None,
    categoria_id: Annotated[
        int | None,
        Query(ge=1, description="Filtra desenhos pela categoria principal."),
    ] = None,
    somente_favoritos: Annotated[
        bool,
        Query(description="Quando verdadeiro, retorna somente desenhos favoritos."),
    ] = False,
    ordenar_por: Annotated[
        CatalogOrderBy,
        Query(description="Campo utilizado na ordenação."),
    ] = CatalogOrderBy.CRIADO_EM,
    ordem: Annotated[
        CatalogOrderDirection,
        Query(description="Direção da ordenação."),
    ] = CatalogOrderDirection.DESC,
    favorito: Annotated[
        bool | None,
        Query(
            description="Filtro legado pelo estado de favorito.",
            deprecated=True,
        ),
    ] = None,
    pagina: Annotated[int, Query(ge=1, description="Página de resultados.")] = 1,
    por_pagina: Annotated[
        int,
        Query(
            ge=1,
            le=CATALOG_MAX_PAGE_SIZE,
            description="Quantidade de cards por página.",
        ),
    ] = CATALOG_DEFAULT_PAGE_SIZE,
) -> CatalogoDesenhosResponse:
    filtros = [Desenho.excluido_em.is_(None)]
    termo = busca.strip() if busca else None
    if termo:
        filtros.append(_filtro_busca(termo))
    if categoria_id is not None:
        filtros.append(Desenho.categoria_id == categoria_id)
    if favorito is not None:
        filtros.append(Desenho.favorito.is_(favorito))
    elif somente_favoritos:
        filtros.append(Desenho.favorito.is_(True))

    ordenacao = _ordenacao_catalogo(ordenar_por, ordem)

    total_query = select(func.count(Desenho.id)).outerjoin(Desenho.categoria).where(*filtros)
    total = (await session.scalar(total_query)) or 0
    query = (
        select(Desenho)
        .outerjoin(Desenho.categoria)
        .options(selectinload(Desenho.categoria))
        .where(*filtros)
        .order_by(*ordenacao)
        .offset((pagina - 1) * por_pagina)
        .limit(por_pagina)
    )
    desenhos = (await session.execute(query)).scalars().all()
    total_paginas = (total + por_pagina - 1) // por_pagina
    return CatalogoDesenhosResponse(
        itens=[_card_desenho(desenho) for desenho in desenhos],
        total=total,
        pagina=pagina,
        por_pagina=por_pagina,
        total_paginas=total_paginas,
        tem_mais=pagina < total_paginas,
    )
