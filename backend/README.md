# Backend — Embroidery Design Catalog

API FastAPI para importar matrizes `.PES`, gerar previews e armazenar os arquivos no MinIO.

## Executar localmente

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
fastapi dev
```

A documentação fica em `http://localhost:8000/docs` e a verificação de saúde em `GET /health`.

## Banco de dados

Com PostgreSQL disponível e `DATABASE_URL` configurada:

```bash
alembic upgrade head
```

O MinIO deve estar disponível nas variáveis `S3_*` antes de enviar arquivos.

## Verificar conexões

Com o ambiente virtual ativado e o `.env` configurado, execute:

```bash
python scripts/test_connections.py
```

O comando testa uma consulta sem escrita no PostgreSQL. No MinIO, ele garante a existência do bucket, envia um arquivo temporário, confirma o envio e o remove ao final.

Resultado esperado:

```text
[OK] PostgreSQL
[OK] MinIO (arquivo enviado e removido)
```
