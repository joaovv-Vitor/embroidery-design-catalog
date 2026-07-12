from app.main import app


def test_us04_routes_are_documented() -> None:
    schema = app.openapi()

    assert "/api/v1/catalogo/desenhos" in schema["paths"]
    assert "/api/v1/desenhos/{desenho_id}" in schema["paths"]
    assert "/api/v1/desenhos/{desenho_id}/favorito" in schema["paths"]
    assert "/api/v1/categorias" in schema["paths"]
    assert "/api/v1/matrizes/{matriz_id}" in schema["paths"]

    operation = schema["paths"]["/api/v1/matrizes/{matriz_id}"]["patch"]
    request_reference = operation["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    request_name = request_reference.rsplit("/", 1)[-1]
    properties = schema["components"]["schemas"][request_name]["properties"]
    assert "identificacao_origem" in properties
    assert "caminho_relativo_origem" in properties
