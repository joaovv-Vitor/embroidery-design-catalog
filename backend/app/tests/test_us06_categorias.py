from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api.routes.v1.categorias import remover_categoria
from app.main import app
from app.schemas.categoria import CriarCategoriaRequest


def test_category_routes_are_documented() -> None:
    schema = app.openapi()

    assert "get" in schema["paths"]["/api/v1/categorias"]
    assert "post" in schema["paths"]["/api/v1/categorias"]
    category_path = schema["paths"]["/api/v1/categorias/{categoria_id}"]
    assert {"get", "patch", "delete"}.issubset(category_path)


def test_category_name_is_required_and_trimmed() -> None:
    category = CriarCategoriaRequest(nome="  Flores  ")

    assert category.nome == "Flores"

    with pytest.raises(ValidationError):
        CriarCategoriaRequest(nome="   ")


def test_category_response_schema_exposes_visual_metadata() -> None:
    schema = app.openapi()
    response_schema = schema["components"]["schemas"]["CategoriaResponse"]

    assert {"id", "nome", "cor", "icone", "criado_em"}.issubset(response_schema["properties"])


class _SessionWithLinkedDrawing:
    def __init__(self) -> None:
        self.committed = False

    async def get(self, _model: object, _category_id: int) -> SimpleNamespace:
        return SimpleNamespace(id=1)

    async def scalar(self, _query: object) -> int:
        return 10

    async def commit(self) -> None:
        self.committed = True


@pytest.mark.asyncio
async def test_category_with_linked_drawings_cannot_be_deleted() -> None:
    session = _SessionWithLinkedDrawing()

    with pytest.raises(HTTPException) as error:
        await remover_categoria(1, session=session)  # type: ignore[arg-type]

    assert error.value.status_code == 409
    assert session.committed is False
