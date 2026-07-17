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


@pytest.mark.asyncio
async def test_list_drawings_filters_by_category_and_new_favorite_parameter() -> None:
    session = _Session(
        [
            SimpleNamespace(
                id=1,
                nome="Flor",
                categoria_id=2,
                favorito=True,
                categoria=None,
                imagem_preview_chave=None,
            ),
        ]
    )

    await pesquisar_desenhos(session=session, categoria_id=2, somente_favoritos=True)

    assert session.query is not None
    assert "desenhos.categoria_id =" in str(session.query)
    assert "desenhos.favorito IS true" in str(session.query)


def test_favorite_routes_are_documented() -> None:
    schema = app.openapi()
    drawings_path = schema["paths"]["/api/v1/catalogo/desenhos"]

    parameters = drawings_path["get"]["parameters"]
    assert any(parameter["name"] == "somente_favoritos" for parameter in parameters)
    favorite_parameter = next(parameter for parameter in parameters if parameter["name"] == "favorito")
    assert favorite_parameter.get("deprecated") is True
    assert "patch" in schema["paths"]["/api/v1/desenhos/{desenho_id}/favorito"]
