from collections.abc import AsyncIterator
from types import SimpleNamespace

import pytest
from botocore.exceptions import ClientError
from fastapi import HTTPException

from app.api.routes.v1 import matrizes


class _Session:
    def __init__(self, matriz: SimpleNamespace) -> None:
        self.matriz = matriz

    async def scalar(self, _query: object) -> SimpleNamespace:
        return self.matriz


class _Storage:
    async def open_object_stream(self, _key: str) -> tuple[str, AsyncIterator[bytes]]:
        async def content() -> AsyncIterator[bytes]:
            yield b"PES original"

        return "application/octet-stream", content()


class _UnavailableStorage:
    async def open_object_stream(self, _key: str) -> tuple[str, AsyncIterator[bytes]]:
        raise ClientError({"Error": {"Code": "NoSuchKey"}}, "GetObject")


def _matriz() -> SimpleNamespace:
    return SimpleNamespace(
        arquivo_backup=SimpleNamespace(
            chave_storage="matrizes/abc.pes",
            nome_original="Zebra 14cm.PES",
            mime_type="application/octet-stream",
        )
    )


@pytest.mark.asyncio
async def test_download_preserves_original_pes_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(matrizes, "ObjectStorage", _Storage)

    response = await matrizes.baixar_matriz(1, session=_Session(_matriz()))  # type: ignore[arg-type]
    content = b"".join([chunk async for chunk in response.body_iterator])

    assert content == b"PES original"
    assert response.headers["content-disposition"] == "attachment; filename*=UTF-8''Zebra%2014cm.PES"


@pytest.mark.asyncio
async def test_download_returns_friendly_message_when_backup_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(matrizes, "ObjectStorage", _UnavailableStorage)

    with pytest.raises(HTTPException) as error:
        await matrizes.baixar_matriz(1, session=_Session(_matriz()))  # type: ignore[arg-type]

    assert error.value.status_code == 404
    assert error.value.detail == "O arquivo de backup desta matriz não está disponível para download."
