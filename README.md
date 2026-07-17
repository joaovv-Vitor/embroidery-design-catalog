# Catálogo de Bordados

Sistema para organizar, localizar e preservar matrizes de bordado `.PES`. O
catálogo transforma arquivos espalhados em pastas e dispositivos em um acervo
visual, com previews, metadados, categorias e backup do arquivo original.

O projeto oferece duas experiências que consomem a mesma API:

- **site web**, para administrar o catálogo e publicar vitrines para clientes;
- **aplicativo Windows**, com acesso controlado a pastas locais e unidades
  removíveis.

## Funcionalidades

- catálogo visual com pesquisa, paginação progressiva, categorias e favoritos;
- importação unitária ou em lote de matrizes `.PES`;
- extração de dimensões, pontos e cores, com geração de preview PNG;
- backup do arquivo original no MinIO e download com o nome preservado;
- edição de metadados, lixeira com restauração e exclusão permanente;
- vitrines temporárias compartilháveis por link e WhatsApp;
- seleção recursiva de pastas e envio para máquina no aplicativo Windows.

Consulte [Funcionalidades](docs/features.md) para conhecer o escopo e as
limitações de cada plataforma.

## Arquitetura

```text
Site Vue ───────┐
                ├──> API FastAPI ──> PostgreSQL
App Tauri/Vue ──┘              └────> MinIO
       │
       └──> recursos locais autorizados do Windows
```

```text
backend/          API, regras de negócio e processamento PES
frontend/         site web publicado com Nginx
app/              aplicativo Windows com Tauri v2
packages/shared/  componentes e serviços compartilhados
docs/             documentação do projeto
```

As fronteiras e decisões técnicas estão em [Arquitetura](docs/architecture.md).

## Início rápido

Pré-requisitos principais: Python 3.11 ou superior, Node.js 20 ou superior,
PostgreSQL e um serviço compatível com S3, como MinIO. O aplicativo desktop
também requer Rust, Tauri v2 e as ferramentas de compilação do Windows.

```bash
git clone <url-do-repositorio>
cd embroidery-design-catalog
npm install
```

O passo a passo completo, incluindo variáveis de ambiente e migrations, está em
[Desenvolvimento](docs/development.md). Com o backend em execução:

- API: `http://localhost:8000`;
- Swagger: `http://localhost:8000/docs`;
- saúde: `http://localhost:8000/health`.

## Status

O núcleo do produto está implementado e é validado primeiro em homologação. A
versão web e o aplicativo Windows permanecem dependentes do backend e não possuem
modo offline nem atualização automática. Suporte a dispositivos classificados
como disco fixo ou MTP está fora do escopo atual.

## Documentação

- [Funcionalidades](docs/features.md)
- [Desenvolvimento local](docs/development.md)
- [Deploy](docs/deployment.md)
- [Aplicativo desktop](docs/desktop.md)
- [API](docs/api.md)
- [Banco e armazenamento](docs/database.md)
- [Testes](docs/testing.md)
- [Contribuição](docs/contributing.md)
- [Segurança](docs/security.md)
- [Guia de screenshots](docs/screenshots/README.md)

## Documentação relacionada

Para preparar um ambiente novo, comece por [Desenvolvimento](docs/development.md).
Para publicar uma versão, consulte [Deploy](docs/deployment.md) e
[Testes](docs/testing.md).
