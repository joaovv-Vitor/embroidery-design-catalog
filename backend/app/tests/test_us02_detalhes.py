from decimal import Decimal
from types import SimpleNamespace

from app.api.routes.v1.desenhos import _detalhe_desenho
from app.main import app


def test_drawing_detail_routes_are_documented() -> None:
    schema = app.openapi()["paths"]

    assert "get" in schema["/api/v1/desenhos/{desenho_id}"]
    assert "get" in schema["/api/v1/desenhos/{desenho_id}/preview"]
    assert "get" in schema["/api/v1/matrizes/{matriz_id}/download"]


def test_drawing_detail_includes_variation_and_origin_metadata() -> None:
    origem = SimpleNamespace(identificacao="Pendrive Azul")
    matriz = SimpleNamespace(
        id=3,
        formato="PES",
        rotulo_tamanho="13 cm",
        largura_mm=Decimal("130.00"),
        altura_mm=Decimal("138.60"),
        quantidade_cores=8,
        quantidade_pontos=21393,
        origem_importacao=origem,
        caminho_relativo_origem="animais/zebra.pes",
    )
    categoria = SimpleNamespace(id=2, nome="Animais", cor="#22c55e", icone="paw-print")
    desenho = SimpleNamespace(
        id=1,
        nome="Zebra",
        categoria_id=2,
        favorito=True,
        descricao="Matriz de zebra",
        categoria=categoria,
        imagem_preview_chave="previews/zebra.png",
        matrizes=[matriz],
    )

    response = _detalhe_desenho(desenho)

    assert response.preview_url == "/api/v1/desenhos/1/preview"
    assert response.categoria.nome == "Animais"
    assert response.matrizes[0].origem_identificacao == "Pendrive Azul"
    assert response.matrizes[0].download_url == "/api/v1/matrizes/3/download"
