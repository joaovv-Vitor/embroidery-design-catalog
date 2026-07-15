from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.api.routes.v1.vitrines_admin import _vitrine_gerencial_response
from app.main import app
from app.models import ItemVitrine, Vitrine
from app.schemas.vitrine import AtualizarStatusVitrineRequest, ConfirmarExclusaoVitrineRequest
from app.services.gerenciamento_vitrine import (
    GerenciamentoVitrineService,
    VitrineAtivaError,
    VitrineExpiradaError,
    calcular_status_vitrine,
)


def _showcase(*, active: bool = True, expired: bool = False) -> Vitrine:
    now = datetime.now(UTC)
    showcase = Vitrine(
        id=1,
        token="management-showcase-token-with-enough-length",
        titulo="Opções para Maria",
        nome_cliente="Maria",
        ativa=active,
        criado_em=now - timedelta(days=1),
        expira_em=now - timedelta(seconds=1) if expired else now + timedelta(days=6),
    )
    showcase.itens = [
        ItemVitrine(
            id=1,
            token="management-item-token-with-enough-length",
            nome_snapshot="Rosa",
            preview_chave_snapshot="vitrines/previews/rosa.png",
        ),
        ItemVitrine(
            id=2,
            token="another-management-item-token-long-enough",
            nome_snapshot="Girassol",
            preview_chave_snapshot=None,
        ),
    ]
    return showcase


class _Session:
    def __init__(self) -> None:
        self.committed = False
        self.deleted: list[object] = []

    async def commit(self) -> None:
        self.committed = True

    async def delete(self, value: object) -> None:
        self.deleted.append(value)


class _Storage:
    def __init__(self) -> None:
        self.deleted: list[str] = []

    def delete_object(self, key: str) -> None:
        self.deleted.append(key)


def test_management_routes_are_documented() -> None:
    paths = app.openapi()["paths"]

    assert {"get", "post"}.issubset(paths["/api/v1/vitrines"])
    assert "patch" in paths["/api/v1/vitrines/{vitrine_id}/status"]
    assert "delete" in paths["/api/v1/vitrines/{vitrine_id}"]


def test_management_actions_require_explicit_confirmation() -> None:
    assert AtualizarStatusVitrineRequest(ativa=False, confirmar=True).confirmar is True
    assert ConfirmarExclusaoVitrineRequest(confirmar=True).confirmar is True

    with pytest.raises(ValidationError):
        AtualizarStatusVitrineRequest(ativa=False, confirmar=False)
    with pytest.raises(ValidationError):
        ConfirmarExclusaoVitrineRequest(confirmar=False)


@pytest.mark.parametrize(
    ("showcase", "expected"),
    [
        (_showcase(), "ativa"),
        (_showcase(expired=True), "expirada"),
        (_showcase(active=False), "desativada"),
    ],
)
def test_showcase_status_is_computed_without_mutation(showcase: Vitrine, expected: str) -> None:
    original_active = showcase.ativa

    assert calcular_status_vitrine(showcase) == expected
    assert showcase.ativa is original_active


def test_management_response_contains_summary_and_link_only_when_active() -> None:
    active = _vitrine_gerencial_response(_showcase())
    expired = _vitrine_gerencial_response(_showcase(expired=True))

    assert active.quantidade_desenhos == 2
    assert active.status == "ativa"
    assert active.link_publico is not None
    assert expired.status == "expirada"
    assert expired.link_publico is None


@pytest.mark.asyncio
async def test_deactivation_interrupts_public_access_immediately() -> None:
    showcase = _showcase()
    session = _Session()

    await GerenciamentoVitrineService(storage=_Storage()).atualizar_status(  # type: ignore[arg-type]
        session,  # type: ignore[arg-type]
        showcase,
        False,
    )

    assert showcase.ativa is False
    assert session.committed is True


@pytest.mark.asyncio
async def test_expired_showcase_cannot_be_reactivated() -> None:
    showcase = _showcase(active=False, expired=True)

    with pytest.raises(VitrineExpiradaError):
        await GerenciamentoVitrineService(storage=_Storage()).atualizar_status(  # type: ignore[arg-type]
            _Session(),  # type: ignore[arg-type]
            showcase,
            True,
        )


@pytest.mark.asyncio
async def test_active_showcase_cannot_be_deleted() -> None:
    with pytest.raises(VitrineAtivaError):
        await GerenciamentoVitrineService(storage=_Storage()).excluir_permanentemente(  # type: ignore[arg-type]
            _Session(),  # type: ignore[arg-type]
            _showcase(),
        )


@pytest.mark.asyncio
async def test_permanent_deletion_removes_only_showcase_and_snapshots(monkeypatch: pytest.MonkeyPatch) -> None:
    showcase = _showcase(active=False)
    session = _Session()
    storage = _Storage()

    async def run_immediately(function: object, *args: object) -> object:
        return function(*args)  # type: ignore[operator]

    monkeypatch.setattr("app.services.gerenciamento_vitrine.asyncio.to_thread", run_immediately)
    await GerenciamentoVitrineService(storage=storage).excluir_permanentemente(  # type: ignore[arg-type]
        session,  # type: ignore[arg-type]
        showcase,
    )

    assert session.deleted == [showcase]
    assert storage.deleted == ["vitrines/previews/rosa.png"]
    assert session.committed is True
