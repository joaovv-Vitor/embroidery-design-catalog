from typing import Annotated

from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.session import DbSession
from app.models import Vitrine
from app.schemas.vitrine import (
    AtualizarStatusVitrineRequest,
    ConfirmarExclusaoVitrineRequest,
    StatusVitrineResponse,
    VitrineGerencialResponse,
)
from app.services.gerenciamento_vitrine import (
    GerenciamentoVitrineService,
    VitrineAtivaError,
    VitrineExpiradaError,
    calcular_status_vitrine,
)

router = APIRouter(prefix="/vitrines", tags=["vitrines compartilhadas"])


def _link_publico(vitrine: Vitrine) -> str:
    base_url = get_settings().api_public_url.rstrip("/")
    return f"{base_url}/api/v1/vitrines/{vitrine.token}/compartilhar"


def _vitrine_gerencial_response(vitrine: Vitrine) -> VitrineGerencialResponse:
    status_vitrine = calcular_status_vitrine(vitrine)
    return VitrineGerencialResponse(
        id=vitrine.id,
        titulo=vitrine.titulo,
        quantidade_desenhos=len(vitrine.itens),
        criado_em=vitrine.criado_em,
        expira_em=vitrine.expira_em,
        status=status_vitrine,
        link_publico=_link_publico(vitrine) if status_vitrine == "ativa" else None,
    )


async def _obter_vitrine(vitrine_id: int, session: DbSession) -> Vitrine:
    query = select(Vitrine).options(selectinload(Vitrine.itens)).where(Vitrine.id == vitrine_id)
    vitrine = await session.scalar(query)
    if vitrine is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vitrine não encontrada.")
    return vitrine


@router.get("")
async def listar_vitrines(session: DbSession) -> list[VitrineGerencialResponse]:
    vitrines = await GerenciamentoVitrineService().listar(session)
    return [_vitrine_gerencial_response(vitrine) for vitrine in vitrines]


@router.patch("/{vitrine_id}/status")
async def atualizar_status_vitrine(
    vitrine_id: Annotated[int, Path(ge=1)],
    dados: AtualizarStatusVitrineRequest,
    session: DbSession,
) -> StatusVitrineResponse:
    vitrine = await _obter_vitrine(vitrine_id, session)
    try:
        await GerenciamentoVitrineService().atualizar_status(session, vitrine, dados.ativa)
    except VitrineExpiradaError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Uma vitrine expirada não pode ser reativada.",
        ) from error
    return StatusVitrineResponse(id=vitrine.id, ativa=vitrine.ativa)


@router.delete("/{vitrine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_vitrine_permanentemente(
    vitrine_id: Annotated[int, Path(ge=1)],
    dados: ConfirmarExclusaoVitrineRequest,
    session: DbSession,
) -> None:
    vitrine = await _obter_vitrine(vitrine_id, session)
    try:
        await GerenciamentoVitrineService().excluir_permanentemente(session, vitrine)
    except VitrineAtivaError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Desative a vitrine antes de excluí-la permanentemente.",
        ) from error
    except ClientError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível remover as previews da vitrine.",
        ) from error
