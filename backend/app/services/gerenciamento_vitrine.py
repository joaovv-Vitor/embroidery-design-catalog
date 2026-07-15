import asyncio
from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Vitrine
from app.services.storage import ObjectStorage

StatusVitrine = Literal["ativa", "expirada", "desativada"]


class VitrineAtivaError(Exception):
    pass


class VitrineExpiradaError(Exception):
    pass


def calcular_status_vitrine(vitrine: Vitrine, agora: datetime | None = None) -> StatusVitrine:
    agora = agora or datetime.now(UTC)
    if not vitrine.ativa:
        return "desativada"
    if vitrine.expira_em <= agora:
        return "expirada"
    return "ativa"


class GerenciamentoVitrineService:
    def __init__(self, storage: ObjectStorage | None = None) -> None:
        self.storage = storage or ObjectStorage()

    async def listar(self, session: AsyncSession) -> list[Vitrine]:
        query = select(Vitrine).options(selectinload(Vitrine.itens)).order_by(Vitrine.criado_em.desc())
        return list((await session.scalars(query)).all())

    async def atualizar_status(self, session: AsyncSession, vitrine: Vitrine, ativa: bool) -> None:
        if ativa and vitrine.expira_em <= datetime.now(UTC):
            raise VitrineExpiradaError
        vitrine.ativa = ativa
        await session.commit()

    async def excluir_permanentemente(self, session: AsyncSession, vitrine: Vitrine) -> None:
        if calcular_status_vitrine(vitrine) == "ativa":
            raise VitrineAtivaError

        preview_keys = {
            item.preview_chave_snapshot for item in vitrine.itens if item.preview_chave_snapshot is not None
        }
        for key in preview_keys:
            await asyncio.to_thread(self.storage.delete_object, key)

        await session.delete(vitrine)
        await session.commit()
