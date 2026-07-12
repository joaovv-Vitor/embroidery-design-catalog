from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.api.routes.v1.desenhos import _recuperavel_ate
from app.main import app
from app.schemas.lixeira import ConfirmarRemocaoRequest


def test_trash_routes_are_documented() -> None:
    schema = app.openapi()["paths"]

    assert "get" in schema["/api/v1/desenhos/lixeira"]
    assert "get" in schema["/api/v1/desenhos/lixeira/{desenho_id}/preview"]
    drawing_path = schema["/api/v1/desenhos/{desenho_id}"]
    assert "delete" in drawing_path
    assert "post" in schema["/api/v1/desenhos/{desenho_id}/restaurar"]
    assert "delete" in schema["/api/v1/desenhos/{desenho_id}/permanente"]


def test_removal_requires_explicit_confirmation() -> None:
    assert ConfirmarRemocaoRequest(confirmar=True).confirmar is True

    with pytest.raises(ValidationError):
        ConfirmarRemocaoRequest(confirmar=False)


def test_trash_retention_period_is_thirty_days_by_default() -> None:
    excluded_at = datetime(2026, 7, 11, tzinfo=UTC)

    assert _recuperavel_ate(excluded_at) == datetime(2026, 8, 10, tzinfo=UTC)


def test_trash_response_exposes_preview_url() -> None:
    schema = app.openapi()["components"]["schemas"]["DesenhoLixeiraResponse"]

    assert "preview_url" in schema["properties"]
