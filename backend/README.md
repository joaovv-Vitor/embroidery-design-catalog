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

## Importação em lote

Use `POST /api/v1/importacoes/lote` com `multipart/form-data`.

- `arquivos`: um ou mais arquivos `.PES`;
- `caminhos_relativos`: JSON opcional; envie um caminho para cada arquivo, na mesma ordem de `arquivos`;
- `identificacao_origem`: opcional, por exemplo `Pendrive Azul`;
- `nome_lote`: opcional.

O frontend pode obter `caminhos_relativos` de `file.webkitRelativePath` ao selecionar uma pasta, quando o navegador oferecer esse campo. Arquivos inválidos são registrados como falha e não interrompem os demais.

O relatório pode ser consultado depois em `GET /api/v1/importacoes/{id}`. Para ajustar informações geradas na importação, use `PATCH /api/v1/importacoes/itens/{item_id}`.

Exemplo com dois arquivos:

```bash
curl -X POST http://localhost:8000/api/v1/importacoes/lote \
  -F 'arquivos=@/caminho/flor.pes' \
  -F 'arquivos=@/caminho/animais/gato.pes' \
  -F 'caminhos_relativos=["flor.pes", "animais/gato.pes"]' \
  -F 'identificacao_origem=Acervo antigo'
```

## Importação de um arquivo

Use `POST /api/v1/importacoes/arquivo` para importar apenas uma matriz:

```bash
curl -X POST http://localhost:8000/api/v1/importacoes/arquivo \
  -F 'arquivo=@/caminho/flor.pes' \
  -F 'identificacao_origem=Pendrive Azul'
```

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

O comando testa a conexão e confirma a existência das tabelas do PostgreSQL. No MinIO, ele garante a existência do bucket, envia um arquivo temporário, confirma o envio e o remove ao final.

Resultado esperado:

```text
[OK] PostgreSQL
[OK] MinIO (arquivo enviado e removido)
```
