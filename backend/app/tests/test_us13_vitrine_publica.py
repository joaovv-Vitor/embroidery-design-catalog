from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException

from app.api.routes.v1.vitrines import _obter_vitrine_valida, _vitrine_publica_response, compartilhar_vitrine
from app.main import app
from app.models import ItemVitrine, Vitrine


def _showcase(*, active: bool = True, expires_at: datetime | None = None) -> Vitrine:
    showcase = Vitrine(
        id=1,
        token="public-showcase-token-with-enough-length",
        titulo="Flores para toalhas",
        nome_cliente="Maria",
        ativa=active,
        criado_em=datetime.now(UTC),
        expira_em=expires_at or datetime.now(UTC) + timedelta(days=7),
    )
    showcase.itens = [
        ItemVitrine(
            id=10,
            token="public-item-token-with-enough-length",
            desenho_id=25,
            nome_snapshot="Rosa delicada",
            preview_chave_snapshot="vitrines/previews/rosa.png",
        )
    ]
    return showcase


class _ShowcaseSession:
    def __init__(self, showcase: Vitrine | None) -> None:
        self.showcase = showcase

    async def scalar(self, _query: object) -> Vitrine | None:
        return self.showcase


def test_public_showcase_routes_are_read_only_and_documented() -> None:
    paths = app.openapi()["paths"]

    public_path = paths["/api/v1/vitrines/{token}"]
    preview_path = paths["/api/v1/vitrines/{token}/itens/{item_token}/preview"]
    status_path = paths["/api/v1/vitrines/{vitrine_id}/status"]

    assert set(public_path) == {"get"}
    assert set(preview_path) == {"get"}
    assert set(status_path) == {"patch"}


def test_public_response_exposes_only_showcase_information() -> None:
    payload = _vitrine_publica_response(_showcase()).model_dump()
    item = payload["itens"][0]

    assert payload["titulo"] == "Flores para toalhas"
    assert payload["nome_cliente"] == "Maria"
    assert item == {
        "numero": 1,
        "nome": "Rosa delicada",
        "preview_url": (
            "/api/v1/vitrines/public-showcase-token-with-enough-length/"
            "itens/public-item-token-with-enough-length/preview"
        ),
    }
    forbidden_fields = {"desenho_id", "item_id", "origem", "hash", "quantidade_pontos", "quantidade_cores"}
    assert forbidden_fields.isdisjoint(item)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("showcase", "message"),
    [
        (_showcase(active=False), "Esta vitrine foi desativada."),
        (_showcase(expires_at=datetime.now(UTC) - timedelta(seconds=1)), "Esta vitrine expirou."),
    ],
)
async def test_inactive_or_expired_showcase_is_unavailable(showcase: Vitrine, message: str) -> None:
    with pytest.raises(HTTPException) as error:
        await _obter_vitrine_valida(showcase.token, _ShowcaseSession(showcase))  # type: ignore[arg-type]

    assert error.value.status_code == 410
    assert error.value.detail == message


@pytest.mark.asyncio
async def test_share_page_contains_open_graph_and_frontend_redirect() -> None:
    showcase = _showcase()

    response = await compartilhar_vitrine(showcase.token, _ShowcaseSession(showcase))  # type: ignore[arg-type]
    html = response.body.decode()

    assert response.status_code == 200
    assert 'property="og:title" content="Flores para toalhas"' in html
    assert 'property="og:description"' in html
    assert 'property="og:image"' in html
    assert f"/vitrines/{showcase.token}" in html


@pytest.mark.asyncio
async def test_share_page_explains_when_showcase_is_disabled() -> None:
    showcase = _showcase(active=False)

    response = await compartilhar_vitrine(showcase.token, _ShowcaseSession(showcase))  # type: ignore[arg-type]

    assert response.status_code == 410
    assert "Vitrine indisponível" in response.body.decode()
    assert "Esta vitrine foi desativada." in response.body.decode()
