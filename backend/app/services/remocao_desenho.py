import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Desenho
from app.services.storage import ObjectStorage


class RemocaoDesenhoService:
    def __init__(self, storage: ObjectStorage | None = None) -> None:
        self.storage = storage or ObjectStorage()

    async def excluir_permanentemente(self, session: AsyncSession, desenho: Desenho) -> None:
        storage_keys = self._storage_keys(desenho)
        for key in storage_keys:
            await asyncio.to_thread(self.storage.delete_object, key)

        for matriz in desenho.matrizes:
            await session.delete(matriz.arquivo_backup)

        await session.delete(desenho)
        await session.commit()

    @staticmethod
    def _storage_keys(desenho: Desenho) -> set[str]:
        keys = {matriz.arquivo_backup.chave_storage for matriz in desenho.matrizes}
        if desenho.imagem_preview_chave:
            keys.add(desenho.imagem_preview_chave)
        return keys
