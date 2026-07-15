import app.models  # noqa: F401
from app.db.base import Base


def test_catalog_schema_is_registered() -> None:
    assert set(Base.metadata.tables) == {
        "arquivos_backup",
        "categorias",
        "desenhos",
        "importacoes",
        "itens_importacao",
        "itens_vitrine",
        "matrizes",
        "origens_importacao",
        "vitrines",
    }


def test_matriz_has_required_foreign_keys() -> None:
    matriz = Base.metadata.tables["matrizes"]

    assert {foreign_key.target_fullname for foreign_key in matriz.foreign_keys} == {
        "arquivos_backup.id",
        "desenhos.id",
        "origens_importacao.id",
    }
