# Arquitetura das aplicações

O Catálogo de Bordados possui três aplicações independentes que compartilham o
mesmo domínio de negócio:

```text
backend/   API FastAPI, banco de dados e armazenamento
frontend/  aplicação web publicada no Dokploy
app/       aplicação desktop Windows construída com Tauri
```

O backend é a única camada responsável por validar e persistir regras de negócio.
As interfaces web e desktop apenas coletam dados, chamam a API e apresentam seus
resultados.

## Fronteiras

### Backend

Responsabilidades:

- validar e processar matrizes `.PES`;
- gerar previews;
- persistir registros no PostgreSQL;
- armazenar arquivos no MinIO;
- controlar catálogo, categorias, favoritos, lixeira e vitrines;
- produzir links públicos e respostas de download.

O backend não deve conhecer APIs do navegador ou do Tauri.

### Frontend web

Responsabilidades:

- disponibilizar o catálogo pelo navegador;
- oferecer a vitrine pública acessada pelos clientes;
- executar o fluxo administrativo pela API;
- selecionar arquivos por recursos permitidos pelo navegador;
- ser compilado em imagem Docker e servido pelo Nginx.

Arquivos de Docker, Nginx e páginas públicas pertencem exclusivamente ao
`frontend`.

### Aplicativo desktop

Responsabilidades:

- reutilizar os fluxos administrativos compatíveis com a versão web;
- acessar recursos locais do Windows por comandos Tauri restritos;
- selecionar e percorrer pastas autorizadas pela usuária;
- iniciar importações usando a mesma API do backend;
- gerar instaladores Windows.

O aplicativo não deve ser implantado como site ou possuir regras de negócio que
divirjam do backend. A camada Rust deve expor apenas operações nativas que não
podem ser realizadas com segurança pelo navegador.

## Código compartilhado

Código independente de plataforma será mantido em `packages/shared`:

- contratos TypeScript da API;
- serviços HTTP que recebem um cliente configurado;
- componentes visuais reutilizáveis;
- composables sem dependência de APIs nativas;
- views administrativas comuns;
- estilos e utilitários puros.

O pacote compartilhado não pode importar:

- `@tauri-apps/*`;
- módulos Rust;
- APIs de Docker ou Nginx;
- configurações específicas de deploy;
- variáveis de ambiente diretamente.

Cada aplicação deverá fornecer seus próprios adaptadores:

```text
frontend/src/platform/  implementações do navegador
app/src/platform/       implementações do Tauri/Windows
```

## Matriz de funcionalidades

| História | Web | Desktop | Observação |
|---|---:|---:|---|
| US01 — Pesquisar desenhos | Sim | Sim | Fluxo compartilhado. |
| US02 — Visualizar detalhes | Sim | Sim | Fluxo compartilhado. |
| US03 — Importar em lote | Limitado | Completo | O desktop usa seleção nativa e leitura recursiva. |
| US04 — Editar desenho | Sim | Sim | Fluxo compartilhado. |
| US05 — Remover desenho | Sim | Sim | Fluxo compartilhado. |
| US06 — Gerenciar categorias | Sim | Sim | Fluxo compartilhado. |
| US07 — Gerenciar favoritos | Sim | Sim | Fluxo compartilhado. |
| US08 — Baixar matriz | Sim | Sim | O desktop poderá usar salvamento nativo. |
| US12 — Criar vitrine | Sim | Sim | Administração compartilhada. |
| US13 — Visualizar vitrine | Sim | Não | Página pública destinada ao navegador do cliente. |
| US14 — Gerenciar vitrines | Sim | Sim | Administração compartilhada. |
| US15 — Enviar para máquina | Não | Sim | Escrita restrita em unidade removível escolhida. |

## Dependências permitidas

```text
frontend ─┐
          ├──> packages/shared ──> backend HTTP API
app ──────┘

app ──> Tauri/Rust ──> recursos locais autorizados
```

Dependências proibidas:

- `frontend` importar código de `app`;
- `packages/shared` importar código de `frontend` ou `app`;
- `frontend` depender de pacotes Tauri;
- o Tauri acessar diretamente PostgreSQL ou MinIO;
- duplicar validações de negócio existentes no backend.

## Segurança do aplicativo desktop

- capabilities devem conceder somente os comandos necessários;
- nenhuma permissão geral de leitura do disco deve ser habilitada;
- caminhos absolutos não devem ser enviados para vitrines ou páginas públicas;
- URLs externas devem ser abertas por um adaptador com destinos permitidos;
- a URL da API deve ser fornecida por `VITE_API_URL` no build;
- o backend deve permitir a origem `http://tauri.localhost` para o aplicativo
  instalado e `http://localhost:5173` durante o desenvolvimento.

## Regras para novas funcionalidades

Antes de implementar uma história, deve-se responder:

1. A funcionalidade depende de um recurso local do Windows?
2. A funcionalidade precisa ser acessada por clientes sem instalar o aplicativo?
3. A lógica pertence ao domínio do backend ou somente à apresentação?

Se depender do Windows, a integração fica em `app/src/platform` ou `app/src-tauri`.
Se precisar ser pública, a entrada fica no `frontend`. Se for regra de negócio,
deve ser implementada no backend e consumida pelas duas interfaces.

## Verificação das fronteiras

Antes de integrar alterações, execute na raiz:

```bash
npm run check
```

Além dos testes automatizados, confirme que:

- `packages/shared` não importa `@tauri-apps/*`;
- `frontend` não importa arquivos de `app`;
- páginas públicas existem somente em `frontend`;
- operações nativas ficam em `app/src/platform` ou `app/src-tauri`;
- somente o `package-lock.json` da raiz é versionado.
