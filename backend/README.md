# Backend — Catálogo de Bordados

API FastAPI responsável por processar matrizes `.PES`, gerar previews, persistir
metadados no PostgreSQL e armazenar arquivos no MinIO.

## Execução rápida

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
fastapi dev
```

No Windows, ative o ambiente com `.\.venv\Scripts\Activate.ps1` e copie o exemplo
com `Copy-Item .env.example .env`.

- Swagger: `http://localhost:8000/docs`;
- OpenAPI: `http://localhost:8000/openapi.json`;
- saúde: `GET http://localhost:8000/health`.

## Conexões

Com PostgreSQL e MinIO configurados no `.env`:

```bash
python scripts/test_connections.py
```

O script testa o banco e realiza o ciclo de envio, verificação e remoção de um
objeto temporário no bucket.

## Documentação relacionada

- [Desenvolvimento](../docs/development.md)
- [API](../docs/api.md)
- [Banco e armazenamento](../docs/database.md)
- [Testes](../docs/testing.md)
- [Segurança](../docs/security.md)
