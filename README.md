# Embroidery Design Catalog

Catálogo de matrizes de bordado. O backend está em [backend](backend/README.md).

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
