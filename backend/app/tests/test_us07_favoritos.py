from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.api.routes.v1.catalogo import pesquisar_desenhos
from app.main import app


class _Result:
    def __init__(self, desenhos: list[SimpleNamespace]) -> None:
        self._desenhos = desenhos

    def scalars(self) -> _Result:
        return self

    def all(self) -> list[SimpleNamespace]:
        return self._desenhos


class _Session:
    def __init__(self, desenhos: list[SimpleNamespace]) -> None:
        self._desenhos = desenhos
        self.query = None

    async def execute(self, query: object) -> _Result:
        self.query = query
        return _Result(self._desenhos)

    async def scalar(self, _query: object) -> int:
        return len(self._desenhos)


@pytest.mark.asyncio
async def test_list_drawings_filters_by_favorite() -> None:
    session = _Session(
        [
            SimpleNamespace(
                id=1,
                nome="Flor",
                categoria_id=None,
                favorito=True,
                categoria=None,
                imagem_preview_chave=None,
            ),
        ]
    )

    response = await pesquisar_desenhos(session=session, favorito=True)

    assert response.itens[0].favorito is True
    assert session.query is not None
    assert "desenhos.favorito IS true" in str(session.query)


def test_favorite_routes_are_documented() -> None:
    schema = app.openapi()
    drawings_path = schema["paths"]["/api/v1/catalogo/desenhos"]

    parameters = drawings_path["get"]["parameters"]
    assert any(parameter["name"] == "favorito" for parameter in parameters)
    assert "patch" in schema["paths"]["/api/v1/desenhos/{desenho_id}/favorito"]
