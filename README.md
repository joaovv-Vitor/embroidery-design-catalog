# Embroidery Design Catalog

Catálogo visual e backup de matrizes de bordado.

## Estrutura do projeto

```text
backend/   API FastAPI, PostgreSQL e MinIO
frontend/  versão web publicada no Dokploy
app/       versão desktop Windows com Tauri v2
```

As decisões sobre responsabilidades, dependências permitidas e distribuição das
histórias de usuário estão documentadas em
[docs/architecture.md](docs/architecture.md).

O backend possui instruções próprias em [backend/README.md](backend/README.md).

## Requisitos

- Node.js 20 ou superior;
- npm 10 ou superior;
- Python 3.11 ou superior para o backend;
- Rust stable e pré-requisitos do Tauri v2 para compilar o desktop;
- Windows 10/11 com WebView2 para gerar e executar o instalador Windows.

Instale todas as dependências JavaScript uma única vez na raiz:

```bash
npm install
```

O repositório utiliza npm workspaces e possui somente um `package-lock.json`, na
raiz. Não execute `npm install` isoladamente dentro de `frontend` ou `app`.

## Desenvolvimento web

Copie `frontend/.env.example` para `frontend/.env.local` e configure a API:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

Execute:

```bash
npm run dev:web
```

A versão web continua responsável pela página pública das vitrines.

## Desenvolvimento desktop

Copie `app/.env.example` para `app/.env.local`. Para usar a API implantada:

```env
VITE_API_URL=https://api.seudominio.com/api/v1
```

No Windows, execute a partir da raiz:

```bash
npm run dev:app
```

O seletor nativo permite somente a pasta escolhida pela usuária. O Rust mantém os
caminhos absolutos em memória e envia ao Vue apenas identificadores, nomes e
caminhos relativos.

## Verificações

```bash
npm test
npm run typecheck
npm run check
```

`npm run check` executa typecheck, testes e builds das camadas web e desktop. Para
validar também a camada Rust, em um computador com Rust instalado:

```bash
cd app/src-tauri
cargo test
cargo clippy -- -D warnings
```

## Instalador Windows

Em um terminal Windows, na raiz do projeto:

```bash
npm install
npm run build:app
```

Os instaladores MSI e NSIS serão gerados em:

```text
app/src-tauri/target/release/bundle/
```

A URL da API é incorporada durante o build pelo `VITE_API_URL`. Gere novamente o
instalador para mudar o ambiente consumido pelo aplicativo.

### Limitações atuais do desktop

- requer conexão com o backend implantado;
- não possui funcionamento offline nem atualização automática;
- não monitora pendrives ou pastas em segundo plano;
- a vitrine pública permanece disponível somente no navegador;
- o instalador Windows deve ser produzido em ambiente Windows compatível.

### Checklist manual do desktop

- [ ] O aplicativo abre e carrega o catálogo pela API configurada.
- [ ] O seletor nativo abre somente após ação da usuária.
- [ ] Uma pasta vazia apresenta uma mensagem clara.
- [ ] Arquivos `.pes` e `.PES` são encontrados recursivamente.
- [ ] Arquivos não PES são ignorados.
- [ ] Nomes e caminhos relativos aparecem antes do envio.
- [ ] É possível cancelar a seleção sem importar.
- [ ] Uma falha de leitura não interrompe os demais arquivos.
- [ ] O relatório apresenta sucessos, falhas e motivos.
- [ ] Nenhum caminho absoluto aparece no catálogo ou nas vitrines.

## Deploy no Dokploy

O arquivo `docker-compose.yml` mantém backend e frontend como serviços separados e
configura `endpoint_mode: dnsrr`, necessário para aplicações Docker Swarm em LXC
do Proxmox.

No Dokploy, crie uma aplicação do tipo **Docker Compose**, selecione esse arquivo
e cadastre os domínios pela aba **Domains**. Configure ao menos estas variáveis de
ambiente na aplicação:

```env
APP_NAME=Embroidery Design Catalog
APP_ENV=production
DATABASE_URL=postgresql+asyncpg://usuario:senha@host:5432/catalogo_bordados
S3_ENDPOINT_URL=https://minio.seudominio.com
S3_ACCESS_KEY=sua_chave
S3_SECRET_KEY=seu_segredo
S3_BUCKET=matrizes-bordado
S3_REGION=us-east-1
TRASH_RETENTION_DAYS=30
CORS_ALLOWED_ORIGINS=["https://app.seudominio.com"]
VITE_API_URL=https://api.seudominio.com/api/v1
```

`CORS_ALLOWED_ORIGINS` recebe a URL pública do frontend. `VITE_API_URL` recebe a
URL pública da API, incluindo o sufixo `/api/v1`, pois é incorporada ao build do
frontend.

O diretório `app` não faz parte do Docker Compose. Ele é compilado separadamente
em um ambiente Windows e consome a mesma API publicada.
