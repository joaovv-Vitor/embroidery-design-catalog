from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.main import app
from app.models import Desenho, Vitrine
from app.schemas.vitrine import CriarVitrineRequest
from app.services.vitrine import DesenhosVitrineNaoEncontradosError, VitrineService


def test_showcase_routes_are_documented() -> None:
    paths = app.openapi()["paths"]

    assert "post" in paths["/api/v1/vitrines"]
    assert "get" in paths["/api/v1/vitrines/{token}"]
    assert "get" in paths["/api/v1/vitrines/{token}/itens/{item_token}/preview"]


def test_showcase_requires_at_least_one_unique_drawing() -> None:
    with pytest.raises(ValidationError):
        CriarVitrineRequest(desenho_ids=[])

    with pytest.raises(ValidationError):
        CriarVitrineRequest(desenho_ids=[1, 1])


def test_showcase_normalizes_optional_information() -> None:
    default_data = CriarVitrineRequest(desenho_ids=[1], titulo="   ", nome_cliente="   ")
    custom_data = CriarVitrineRequest(desenho_ids=[1], titulo="  Flores  ", nome_cliente="  Maria  ")

    assert default_data.titulo == "Opções de bordado"
    assert default_data.nome_cliente is None
    assert custom_data.titulo == "Flores"
    assert custom_data.nome_cliente == "Maria"


def test_showcase_models_keep_snapshot_and_nullable_catalog_reference() -> None:
    item_relationship = Vitrine.itens.property
    drawing_id = next(
        column for column in Vitrine.metadata.tables["itens_vitrine"].columns if column.name == "desenho_id"
    )
    foreign_key = next(iter(drawing_id.foreign_keys))

    assert "delete-orphan" in item_relationship.cascade
    assert drawing_id.nullable is True
    assert foreign_key.ondelete == "SET NULL"


class _ScalarsResult:
    def __init__(self, drawings: list[Desenho]) -> None:
        self.drawings = drawings

    def all(self) -> list[Desenho]:
        return self.drawings


class _ShowcaseSession:
    def __init__(self, drawings: list[Desenho]) -> None:
        self.drawings = drawings
        self.added: Vitrine | None = None
        self.committed = False
        self.rolled_back = False

    async def scalars(self, _query: object) -> _ScalarsResult:
        return _ScalarsResult(self.drawings)

    def add(self, showcase: Vitrine) -> None:
        self.added = showcase

    async def commit(self) -> None:
        self.committed = True
        assert self.added is not None
        self.added.id = 1
        self.added.criado_em = datetime.now(UTC)
        for index, item in enumerate(self.added.itens, start=1):
            item.id = index
            item.vitrine_id = self.added.id
            item.desenho_id = item.desenho.id

    async def refresh(self, _showcase: Vitrine, attribute_names: list[str]) -> None:
        assert attribute_names == ["itens"]

    async def rollback(self) -> None:
        self.rolled_back = True


class _Storage:
    def __init__(self) -> None:
        self.copies: list[tuple[str, str]] = []
        self.deleted: list[str] = []

    def copy_object(self, source_key: str, destination_key: str) -> None:
        self.copies.append((source_key, destination_key))

    def delete_object(self, key: str) -> None:
        self.deleted.append(key)


class _TestShowcaseService(VitrineService):
    async def _copiar_preview(self, source_key: str | None) -> str | None:
        if source_key is None:
            return None
        destination_key = "vitrines/previews/snapshot.png"
        self.storage.copy_object(source_key, destination_key)
        return destination_key


@pytest.mark.asyncio
async def test_showcase_creation_preserves_name_and_preview() -> None:
    drawing = Desenho(id=1, nome="Zebra 14cm", imagem_preview_chave="previews/zebra.png", favorito=False)
    session = _ShowcaseSession([drawing])
    storage = _Storage()
    before = datetime.now(UTC) + timedelta(days=7)

    showcase = await _TestShowcaseService(storage=storage).criar(  # type: ignore[arg-type]
        session,  # type: ignore[arg-type]
        CriarVitrineRequest(desenho_ids=[1]),
    )

    assert showcase.titulo == "Opções de bordado"
    assert showcase.expira_em >= before
    assert len(showcase.token) >= 32
    assert showcase.itens[0].nome_snapshot == "Zebra 14cm"
    assert len(showcase.itens[0].token) >= 20
    assert showcase.itens[0].preview_chave_snapshot.startswith("vitrines/previews/")
    assert storage.copies[0][0] == "previews/zebra.png"
    assert session.committed is True


@pytest.mark.asyncio
async def test_showcase_rejects_missing_or_trashed_drawings() -> None:
    session = _ShowcaseSession([])

    with pytest.raises(DesenhosVitrineNaoEncontradosError) as error:
        await VitrineService(storage=SimpleNamespace()).criar(  # type: ignore[arg-type]
            session,  # type: ignore[arg-type]
            CriarVitrineRequest(desenho_ids=[7]),
        )

    assert error.value.desenho_ids == [7]
    assert session.committed is False
