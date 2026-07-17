# Desenvolvimento local

## Pré-requisitos

- Git;
- Python 3.11 ou superior; a imagem do backend usa Python 3.12;
- Node.js 20 ou superior e npm 10 ou superior;
- PostgreSQL acessível pela aplicação;
- MinIO ou outro serviço compatível com S3;
- para o desktop: Rust stable, WebView2 e pré-requisitos do Tauri v2 no Windows.

O `docker-compose.yml` do repositório é destinado ao Dokploy e depende da rede
externa `dokploy-network`. Ele não provisiona PostgreSQL ou MinIO para o ambiente
local.

## Clonar e instalar dependências JavaScript

```bash
git clone <url-do-repositorio>
cd embroidery-design-catalog
npm install
```

O projeto utiliza npm workspaces e mantém apenas um `package-lock.json`, na raiz.
Não execute `npm install` isoladamente em `frontend/` ou `app/`.

## Backend

No Linux ou macOS:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
fastapi dev
```

No PowerShell, a ativação do ambiente é:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
fastapi dev
```

Serviços disponíveis:

- API: `http://localhost:8000`;
- Swagger: `http://localhost:8000/docs`;
- OpenAPI: `http://localhost:8000/openapi.json`;
- health check: `http://localhost:8000/health`.

### Variáveis do backend

Copie `backend/.env.example` para `backend/.env` e substitua apenas com valores do
seu ambiente. O arquivo `.env` é ignorado pelo Git.

| Variável | Finalidade |
|---|---|
| `APP_NAME` | Nome exibido pela API. |
| `APP_ENV` | Identificação do ambiente. |
| `DATABASE_URL` | Conexão assíncrona PostgreSQL/asyncpg. |
| `S3_ENDPOINT_URL` | Endpoint do MinIO/S3. |
| `S3_ACCESS_KEY` | Chave de acesso do storage. |
| `S3_SECRET_KEY` | Segredo do storage. |
| `S3_BUCKET` | Bucket dos backups e previews. |
| `S3_REGION` | Região informada ao cliente S3. |
| `API_PUBLIC_URL` | URL pública usada na criação de links de vitrine. |
| `FRONTEND_PUBLIC_URL` | URL pública usada para abrir a vitrine no site. |
| `TRASH_RETENTION_DAYS` | Prazo de recuperação da lixeira. |
| `CORS_ALLOWED_ORIGINS` | Lista JSON de origens autorizadas pelo navegador. |

O limite de upload atual é de 50 MiB por arquivo e está definido na configuração
do backend, não no `.env.example`.

### Testar PostgreSQL e MinIO

Com o ambiente virtual ativo e o `.env` configurado:

```bash
python scripts/test_connections.py
```

O script verifica o PostgreSQL e, no MinIO, cria o bucket quando necessário,
envia um objeto temporário, confirma sua existência e o remove.

## Site web

Copie `frontend/.env.example` para `frontend/.env.local`:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

Na raiz do repositório:

```bash
npm run dev:web
```

O Vite usa normalmente `http://localhost:5173`. Essa origem deve estar presente
em `CORS_ALLOWED_ORIGINS` no backend.

## Aplicativo desktop

Copie `app/.env.example` para `app/.env.local` e configure a mesma API:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

No Windows, a partir da raiz:

```powershell
npm run dev:app
```

Para consumir uma API implantada, altere apenas `VITE_API_URL`. A origem do
WebView do Tauri também precisa estar autorizada pelo CORS do backend. Consulte
[Aplicativo desktop](desktop.md).

## Migrations

Com `DATABASE_URL` configurada e o diretório atual em `backend/`:

```bash
alembic upgrade head
```

Ao criar uma nova migration, revise o arquivo gerado antes de aplicá-lo. Não use
credenciais de produção no ambiente de desenvolvimento.

## Documentação relacionada

- [Testes](testing.md)
- [API](api.md)
- [Banco e armazenamento](database.md)
- [Deploy](deployment.md)
- [Aplicativo desktop](desktop.md)
