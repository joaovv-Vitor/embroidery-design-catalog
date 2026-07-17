from types import SimpleNamespace

from app.api.routes.v1.catalogo import _card_desenho, _filtro_busca, _ordenacao_catalogo
from app.main import app
from app.schemas.desenho import (
    CATALOG_DEFAULT_PAGE_SIZE,
    CATALOG_MAX_PAGE_SIZE,
    CatalogoDesenhosResponse,
    CatalogOrderBy,
    CatalogOrderDirection,
)


def test_catalog_search_parameters_are_documented() -> None:
    schema = app.openapi()
    parameters = schema["paths"]["/api/v1/catalogo/desenhos"]["get"]["parameters"]
    parameter_names = {parameter["name"] for parameter in parameters}

    assert {
        "busca",
        "categoria_id",
        "somente_favoritos",
        "ordenar_por",
        "ordem",
        "favorito",
        "pagina",
        "por_pagina",
    }.issubset(parameter_names)
    page_size = next(parameter for parameter in parameters if parameter["name"] == "por_pagina")

    assert page_size["schema"]["default"] == CATALOG_DEFAULT_PAGE_SIZE
    assert page_size["schema"]["maximum"] == CATALOG_MAX_PAGE_SIZE


def test_search_filter_matches_drawing_and_category_names() -> None:
    query = str(_filtro_busca("zebra"))

    assert "desenhos.nome" in query
    assert "categorias.nome" in query
    assert "LIKE" in query


def test_catalog_ordering_is_limited_and_deterministic() -> None:
    nome_ascendente = _ordenacao_catalogo(CatalogOrderBy.NOME, CatalogOrderDirection.ASC)
    criado_descendente = _ordenacao_catalogo(CatalogOrderBy.CRIADO_EM, CatalogOrderDirection.DESC)

    assert "desenhos.nome ASC" in str(nome_ascendente[0])
    assert "desenhos.id ASC" in str(nome_ascendente[1])
    assert "desenhos.criado_em DESC" in str(criado_descendente[0])
    assert "desenhos.id DESC" in str(criado_descendente[1])


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


def test_catalog_response_includes_pagination_metadata() -> None:
    response = CatalogoDesenhosResponse(
        itens=[],
        total=49,
        pagina=1,
        por_pagina=24,
        total_paginas=3,
        tem_mais=True,
    )

    assert response.total_paginas == 3
    assert response.tem_mais is True
