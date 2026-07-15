import asyncio
import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Desenho, ItemVitrine, Vitrine
from app.schemas.vitrine import CriarVitrineRequest
from app.services.storage import ObjectStorage

VALIDADE_PADRAO_DIAS = 7


class DesenhosVitrineNaoEncontradosError(Exception):
    def __init__(self, desenho_ids: list[int]) -> None:
        self.desenho_ids = desenho_ids
        super().__init__("Um ou mais desenhos não foram encontrados no catálogo.")


class VitrineService:
    def __init__(self, storage: ObjectStorage | None = None) -> None:
        self.storage = storage or ObjectStorage()

    async def criar(self, session: AsyncSession, dados: CriarVitrineRequest) -> Vitrine:
        desenhos = await self._obter_desenhos_ativos(session, dados.desenho_ids)
        desenhos_por_id = {desenho.id: desenho for desenho in desenhos}
        ids_ausentes = [desenho_id for desenho_id in dados.desenho_ids if desenho_id not in desenhos_por_id]
        if ids_ausentes:
            raise DesenhosVitrineNaoEncontradosError(ids_ausentes)

        chaves_copiadas: list[str] = []
        try:
            vitrine = Vitrine(
                token=secrets.token_urlsafe(32),
                titulo=dados.titulo,
                nome_cliente=dados.nome_cliente,
                expira_em=datetime.now(UTC) + timedelta(days=VALIDADE_PADRAO_DIAS),
            )
            session.add(vitrine)

            for desenho_id in dados.desenho_ids:
                desenho = desenhos_por_id[desenho_id]
                preview_snapshot = await self._copiar_preview(desenho.imagem_preview_chave)
                if preview_snapshot is not None:
                    chaves_copiadas.append(preview_snapshot)
                vitrine.itens.append(
                    ItemVitrine(
                        desenho=desenho,
                        token=secrets.token_urlsafe(24),
                        nome_snapshot=desenho.nome,
                        preview_chave_snapshot=preview_snapshot,
                    )
                )

            await session.commit()
            await session.refresh(vitrine, attribute_names=["itens"])
            return vitrine
        except Exception:
            await session.rollback()
            await self._remover_copias(chaves_copiadas)
            raise

    async def _obter_desenhos_ativos(self, session: AsyncSession, desenho_ids: list[int]) -> list[Desenho]:
        query = select(Desenho).where(Desenho.id.in_(desenho_ids), Desenho.excluido_em.is_(None))
        return list((await session.scalars(query)).all())

    async def _copiar_preview(self, source_key: str | None) -> str | None:
        if source_key is None:
            return None
        destination_key = f"vitrines/previews/{uuid4()}.png"
        await asyncio.to_thread(self.storage.copy_object, source_key, destination_key)
        return destination_key

    async def _remover_copias(self, keys: list[str]) -> None:
        await asyncio.gather(
            *(asyncio.to_thread(self.storage.delete_object, key) for key in keys),
            return_exceptions=True,
        )
