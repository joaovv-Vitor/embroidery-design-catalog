import pytest
from fastapi import HTTPException

from app.api.routes.v1.importacoes import _parse_caminhos_relativos
from app.main import app


def test_batch_import_route_is_documented() -> None:
    schema = app.openapi()

    assert "/api/v1/importacoes/lote" in schema["paths"]
    assert "post" in schema["paths"]["/api/v1/importacoes/lote"]

    request_schema = schema["paths"]["/api/v1/importacoes/lote"]["post"]["requestBody"]["content"][
        "multipart/form-data"
    ]["schema"]
    body_name = request_schema["$ref"].rsplit("/", 1)[-1]
    file_items = schema["components"]["schemas"][body_name]["properties"]["arquivos"]["items"]

    assert file_items == {"type": "string", "format": "binary"}


def test_single_file_import_route_is_documented() -> None:
    schema = app.openapi()

    assert "/api/v1/importacoes/arquivo" in schema["paths"]
    assert "post" in schema["paths"]["/api/v1/importacoes/arquivo"]


def test_parse_relative_paths_json() -> None:
    assert _parse_caminhos_relativos('["flor.pes", "animais/gato.pes"]') == [
        "flor.pes",
        "animais/gato.pes",
    ]
    assert _parse_caminhos_relativos("[]") is None


def test_rejects_invalid_relative_paths_json() -> None:
    with pytest.raises(HTTPException) as error:
        _parse_caminhos_relativos("flor.pes")

    assert error.value.status_code == 422
