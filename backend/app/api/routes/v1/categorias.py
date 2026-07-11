from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import select

from app.db.session import DbSession
from app.models import Categoria, Desenho
from app.schemas.categoria import AtualizarCategoriaRequest, CategoriaResponse, CriarCategoriaRequest

router = APIRouter(prefix="/categorias", tags=["categorias"])


def _categoria_response(categoria: Categoria) -> CategoriaResponse:
    return CategoriaResponse(
        id=categoria.id,
        nome=categoria.nome,
        cor=categoria.cor,
        icone=categoria.icone,
        criado_em=categoria.criado_em,
    )


async def _obter_categoria(categoria_id: int, session: DbSession) -> Categoria:
    categoria = await session.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    return categoria


async def _validar_nome_disponivel(nome: str, session: DbSession, categoria_id: int | None = None) -> None:
    query = select(Categoria.id).where(Categoria.nome == nome)
    if categoria_id is not None:
        query = query.where(Categoria.id != categoria_id)

    if await session.scalar(query) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe uma categoria com este nome.")


@router.get("")
async def listar_categorias(session: DbSession) -> list[CategoriaResponse]:
    categorias = (await session.execute(select(Categoria).order_by(Categoria.nome))).scalars().all()
    return [_categoria_response(categoria) for categoria in categorias]


@router.post("", status_code=status.HTTP_201_CREATED)
async def criar_categoria(dados: CriarCategoriaRequest, session: DbSession) -> CategoriaResponse:
    await _validar_nome_disponivel(dados.nome, session)

    categoria = Categoria(**dados.model_dump())
    session.add(categoria)
    await session.commit()
    await session.refresh(categoria)
    return _categoria_response(categoria)


@router.get("/{categoria_id}")
async def obter_categoria(
    categoria_id: Annotated[int, Path(ge=1)],
    session: DbSession,
) -> CategoriaResponse:
    return _categoria_response(await _obter_categoria(categoria_id, session))


@router.patch("/{categoria_id}")
async def atualizar_categoria(
    categoria_id: Annotated[int, Path(ge=1)],
    dados: AtualizarCategoriaRequest,
    session: DbSession,
) -> CategoriaResponse:
    categoria = await _obter_categoria(categoria_id, session)
    valores = dados.model_dump(exclude_unset=True)

    if "nome" in valores:
        await _validar_nome_disponivel(valores["nome"], session, categoria_id)

    for campo, valor in valores.items():
        setattr(categoria, campo, valor)

    await session.commit()
    await session.refresh(categoria)
    return _categoria_response(categoria)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_categoria(
    categoria_id: Annotated[int, Path(ge=1)],
    session: DbSession,
) -> None:
    categoria = await _obter_categoria(categoria_id, session)
    desenho_vinculado = await session.scalar(select(Desenho.id).where(Desenho.categoria_id == categoria_id).limit(1))
    if desenho_vinculado is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A categoria possui desenhos vinculados. Reclassifique-os antes de excluí-la.",
        )

    await session.delete(categoria)
    await session.commit()
