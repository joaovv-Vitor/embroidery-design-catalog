# Deploy

O deploy atual publica backend e site como serviços separados no Dokploy. O
aplicativo Windows é compilado fora do servidor e não faz parte do Compose.

## Ambientes e branches

- `main`: versão estável destinada à produção;
- `homolog`: ambiente de validação antes da produção;
- `feature/*`, `fix/*` e `hotfix/*`: branches temporárias de trabalho.

Uma alteração deve ser validada em `homolog` antes do merge e deploy em `main`
quando afetar comportamento do produto, dados ou infraestrutura.

## Docker Compose no Dokploy

O arquivo `docker-compose.yml`:

- constrói o backend a partir de `backend/Dockerfile`;
- constrói o site a partir de `frontend/Dockerfile`, usando a raiz como contexto;
- injeta `VITE_API_URL` durante o build do Vite;
- conecta os serviços à rede externa `dokploy-network`;
- configura `endpoint_mode: dnsrr` para o ambiente Docker Swarm em LXC.

Crie uma aplicação **Docker Compose** no Dokploy, selecione a branch do ambiente e
aponte para `docker-compose.yml`. Configure os domínios pela aba **Domains**:

- backend: porta interna `8000`;
- frontend: porta interna `80`.

O DNS público deve apontar para o servidor do Dokploy. Não versione labels,
certificados ou endereços específicos do ambiente quando eles forem administrados
pelo painel.

## Variáveis de ambiente

Configure no Dokploy, sem adicionar valores reais ao repositório:

```env
APP_NAME=Embroidery Design Catalog
APP_ENV=production
DATABASE_URL=postgresql+asyncpg://usuario:senha@host:5432/catalogo_bordados
S3_ENDPOINT_URL=https://minio.seudominio.com
S3_ACCESS_KEY=trocar_por_chave
S3_SECRET_KEY=trocar_por_segredo
S3_BUCKET=matrizes-bordado
S3_REGION=us-east-1
API_PUBLIC_URL=https://api.seudominio.com
FRONTEND_PUBLIC_URL=https://app.seudominio.com
TRASH_RETENTION_DAYS=30
CORS_ALLOWED_ORIGINS=["https://app.seudominio.com"]
VITE_API_URL=https://api.seudominio.com/api/v1
```

`CORS_ALLOWED_ORIGINS` recebe origens do site e, quando aplicável, do WebView
desktop. `VITE_API_URL` é argumento de build: sua alteração exige reconstruir a
imagem do frontend.

## Sequência de publicação

1. Execute as verificações descritas em [Testes](testing.md).
2. Faça backup do PostgreSQL e confirme a política de backup do bucket.
3. Faça merge na branch do ambiente correspondente.
4. Inicie o deploy e acompanhe os logs dos dois serviços.
5. No terminal do container backend, execute:

   ```bash
   cd /app
   alembic upgrade head
   ```

6. Execute a validação pós-deploy.

O container usa `/app` como diretório de trabalho. Executar o Alembic a partir de
`/` não encontra o `alembic.ini`.

## Validação pós-deploy

- `GET /health` responde `200` com `{"status":"ok"}`;
- Swagger/OpenAPI abre no domínio da API, quando não bloqueado externamente;
- catálogo retorna no máximo 24 itens na primeira página padrão;
- previews, filtros e ação **Carregar mais desenhos** funcionam;
- importação de um arquivo de teste grava banco e storage;
- download preserva o nome original;
- frontend não apresenta erros de CORS;
- criação e abertura pública de vitrine usam os domínios corretos.

## Rollback

Não há script automatizado de rollback no repositório. Para código, reverta o
commit ou PR problemático e faça novo deploy da branch estável. Para banco:

1. interrompa novas operações de escrita;
2. avalie a compatibilidade da migration antes de executar downgrade;
3. prefira restaurar o backup validado quando houver risco de perda;
4. mantenha banco e objetos MinIO consistentes durante a recuperação.

Não execute downgrade destrutivo ou restauração diretamente em produção sem
backup e validação prévia em homologação.

## Instalador Windows

O instalador não é gerado pelo Compose. Em um computador Windows configurado:

```powershell
npm install
npm run build:app
```

Os bundles MSI e NSIS ficam em:

```text
app/src-tauri/target/release/bundle/
```

`VITE_API_URL` é incorporada ao build; gere outro instalador para trocar o
ambiente consumido pelo aplicativo.

## Documentação relacionada

- [Desenvolvimento](development.md)
- [Testes](testing.md)
- [Segurança](security.md)
- [Aplicativo desktop](desktop.md)
