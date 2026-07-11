from app.main import app


def test_us04_routes_are_documented() -> None:
    schema = app.openapi()

    assert "/api/v1/desenhos" in schema["paths"]
    assert "/api/v1/desenhos/{desenho_id}" in schema["paths"]
    assert "/api/v1/desenhos/{desenho_id}/favorito" in schema["paths"]
    assert "/api/v1/categorias" in schema["paths"]
    assert "/api/v1/matrizes/{matriz_id}" in schema["paths"]
