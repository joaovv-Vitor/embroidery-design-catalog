from types import SimpleNamespace

from app.api.routes.v1.catalogo import _card_desenho, _filtro_busca
from app.main import app


def test_catalog_search_parameters_are_documented() -> None:
    schema = app.openapi()
    parameters = schema["paths"]["/api/v1/catalogo/desenhos"]["get"]["parameters"]
    parameter_names = {parameter["name"] for parameter in parameters}

    assert {"busca", "favorito", "pagina", "por_pagina"}.issubset(parameter_names)


def test_search_filter_matches_drawing_and_category_names() -> None:
    query = str(_filtro_busca("zebra"))

    assert "desenhos.nome" in query
    assert "categorias.nome" in query
    assert "LIKE" in query


def test_catalog_card_exposes_preview_name_and_category() -> None:
    categoria = SimpleNamespace(id=2, nome="Animais", cor="#22c55e", icone="paw-print")
    desenho = SimpleNamespace(
        id=1,
        nome="Zebra",
        favorito=False,
        categoria=categoria,
        imagem_preview_chave="previews/zebra.png",
    )

    card = _card_desenho(desenho)

    assert card.nome == "Zebra"
    assert card.categoria.nome == "Animais"
    assert card.preview_url == "/api/v1/desenhos/1/preview"
