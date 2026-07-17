from types import SimpleNamespace

import pytest
from fastapi.responses import StreamingResponse

from app.api.routes.v1.desenhos import _preview_cache_headers, visualizar_preview
from app.services.storage import ObjectStorage


class FakeSession:
    def __init__(self, desenho: object) -> None:
        self.desenho = desenho

    async def scalar(self, _query: object) -> object:
        return self.desenho


async def _preview_content():
    yield b"preview"


@pytest.mark.asyncio
async def test_preview_returns_cache_headers() -> None:
    desenho = SimpleNamespace(id=1, excluido_em=None, imagem_preview_chave="previews/preview-1.png")

    async def open_object_stream(_self: ObjectStorage, _key: str):
        return "image/png", _preview_content()

    original_open_object_stream = ObjectStorage.open_object_stream
    ObjectStorage.open_object_stream = open_object_stream
    try:
        response = await visualizar_preview(1, FakeSession(desenho))
    finally:
        ObjectStorage.open_object_stream = original_open_object_stream

    assert isinstance(response, StreamingResponse)
    assert response.headers["cache-control"] == "public, max-age=86400, stale-while-revalidate=604800"
    assert response.headers["etag"] == _preview_cache_headers(desenho.imagem_preview_chave)["ETag"]


@pytest.mark.asyncio
async def test_preview_returns_not_modified_for_matching_etag() -> None:
    desenho = SimpleNamespace(id=1, excluido_em=None, imagem_preview_chave="previews/preview-1.png")
    etag = _preview_cache_headers(desenho.imagem_preview_chave)["ETag"]

    response = await visualizar_preview(1, FakeSession(desenho), if_none_match=etag)

    assert response.status_code == 304
    assert response.headers["etag"] == etag
