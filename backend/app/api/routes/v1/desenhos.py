from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import DbSession
from app.models import Categoria, Desenho
from app.schemas.desenho import AtualizarDesenhoRequest, AtualizarFavoritoRequest, DesenhoResumoResponse

router = APIRouter(prefix="/desenhos", tags=["desenhos"])


@router.get("")
async def listar_desenhos(
    session: DbSession,
    favorito: Annotated[
        bool | None,
        Query(description="Filtra desenhos pelo estado de favorito."),
    ] = None,
) -> list[DesenhoResumoResponse]:
    query = select(Desenho).options(selectinload(Desenho.categoria))
    if favorito is not None:
        query = query.where(Desenho.favorito.is_(favorito))

    desenhos = (await session.execute(query)).scalars().all()
    return [
        DesenhoResumoResponse(
            id=desenho.id,
            nome=desenho.nome,
            categoria_id=desenho.categoria_id,
            favorito=desenho.favorito,
        )
        for desenho in desenhos
    ]


@router.get("/{desenho_id}")
async def obter_desenho(
    desenho_id: Annotated[int, Path(ge=1)],
    session: DbSession,
) -> DesenhoResumoResponse:
    desenho = await session.get(Desenho, desenho_id)
    if desenho is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Desenho não encontrado.")
    return DesenhoResumoResponse(
        id=desenho.id,
        nome=desenho.nome,
        categoria_id=desenho.categoria_id,
        favorito=desenho.favorito,
    )


@router.patch("/{desenho_id}")
async def atualizar_desenho(
    desenho_id: Annotated[int, Path(ge=1)],
    dados: AtualizarDesenhoRequest,
    session: DbSession,
) -> DesenhoResumoResponse:
    desenho = await session.get(Desenho, desenho_id)
    if desenho is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Desenho não encontrado.")

    valores = dados.model_dump(exclude_unset=True)
    if "nome" in valores:
        desenho.nome = valores["nome"]
    if "categoria_id" in valores:
        categoria_id = valores["categoria_id"]
        if categoria_id is not None and await session.get(Categoria, categoria_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
        desenho.categoria_id = valores["categoria_id"]

    await session.commit()
    return DesenhoResumoResponse(
        id=desenho.id,
        nome=desenho.nome,
        categoria_id=desenho.categoria_id,
        favorito=desenho.favorito,
    )


@router.patch("/{desenho_id}/favorito")
async def atualizar_favorito(
    desenho_id: Annotated[int, Path(ge=1)],
    dados: AtualizarFavoritoRequest,
    session: DbSession,
) -> DesenhoResumoResponse:
    desenho = await session.get(Desenho, desenho_id)
    if desenho is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Desenho não encontrado.")

    desenho.favorito = dados.favorito
    await session.commit()
    return DesenhoResumoResponse(
        id=desenho.id,
        nome=desenho.nome,
        categoria_id=desenho.categoria_id,
        favorito=desenho.favorito,
    )


@router.delete("/{desenho_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_desenho(
    desenho_id: Annotated[int, Path(ge=1)],
    session: DbSession,
) -> None:
    desenho = await session.get(Desenho, desenho_id)
    if desenho is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Desenho não encontrado.")

    await session.delete(desenho)
    await session.commit()
