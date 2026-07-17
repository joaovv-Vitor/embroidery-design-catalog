# API

O backend FastAPI expõe a documentação OpenAPI automaticamente. Em ambiente
local:

- Swagger UI: `http://localhost:8000/docs`;
- esquema OpenAPI: `http://localhost:8000/openapi.json`;
- health check: `GET http://localhost:8000/health`.

Com exceção de `/health`, as rotas da aplicação usam o prefixo `/api/v1`.

## Grupos de endpoints

| Grupo | Rotas principais | Responsabilidade |
|---|---|---|
| Catálogo | `GET /catalogo/desenhos` | Pesquisa, filtros, ordenação e paginação. |
| Categorias | `GET/POST /categorias`, `GET/PATCH/DELETE /categorias/{id}` | Gerenciamento das categorias. |
| Desenhos | `GET/PATCH/DELETE /desenhos/{id}` | Detalhes, edição e envio à lixeira. |
| Favoritos | `PATCH /desenhos/{id}/favorito` | Favoritar ou desfavoritar. |
| Lixeira | `GET /desenhos/lixeira`, `POST /desenhos/{id}/restaurar`, `DELETE /desenhos/{id}/permanente` | Recuperação e exclusão definitiva. |
| Importações | `POST /importacoes/arquivo`, `POST /importacoes/lote`, `GET /importacoes/{id}` | Importação e relatório. |
| Matrizes | `GET /matrizes/{id}/download`, `PATCH /matrizes/{id}` | Download original e edição da origem. |
| Vitrines públicas | `POST /vitrines`, `GET /vitrines/{token}` | Criação e visualização por token. |
| Gestão de vitrines | `GET /vitrines`, `PATCH /vitrines/{id}/status`, `DELETE /vitrines/{id}` | Listagem, desativação e exclusão. |

Use o Swagger para consultar schemas, campos obrigatórios, respostas e códigos de
erro atualizados.

## Catálogo paginado

Exemplo:

```http
GET /api/v1/catalogo/desenhos?pagina=1&por_pagina=24&busca=flor&categoria_id=2&somente_favoritos=false&ordenar_por=criado_em&ordem=desc
```

Parâmetros suportados:

- `pagina`: começa em 1;
- `por_pagina`: padrão 24, máximo 50;
- `busca`: nome do desenho ou categoria, até 120 caracteres;
- `categoria_id`: categoria principal;
- `somente_favoritos`: filtro booleano;
- `ordenar_por`: `nome`, `criado_em` ou `atualizado_em`;
- `ordem`: `asc` ou `desc`.

A resposta contém `itens`, `total`, `pagina`, `por_pagina`, `total_paginas` e
`tem_mais`. A ordenação usa o ID como desempate para manter a paginação
determinística.

```bash
curl "http://localhost:8000/api/v1/catalogo/desenhos?pagina=1&por_pagina=24"
```

## Importação em lote

`POST /api/v1/importacoes/lote` recebe `multipart/form-data`:

- `arquivos`: um ou mais arquivos `.PES`;
- `caminhos_relativos`: JSON opcional, na mesma ordem dos arquivos;
- `identificacao_origem`: texto opcional;
- `nome_lote`: texto opcional.

```bash
curl -X POST http://localhost:8000/api/v1/importacoes/lote \
  -F 'arquivos=@/caminho/flor.pes' \
  -F 'arquivos=@/caminho/animais/gato.pes' \
  -F 'caminhos_relativos=["flor.pes", "animais/gato.pes"]' \
  -F 'identificacao_origem=Acervo antigo'
```

Cada arquivo é processado isoladamente. O relatório pode ser consultado depois
em `GET /api/v1/importacoes/{id}`.

## Previews e downloads

- `GET /api/v1/desenhos/{id}/preview` entrega o preview ativo com `ETag` e
  `Cache-Control`;
- `GET /api/v1/desenhos/lixeira/{id}/preview` entrega o preview da lixeira;
- `GET /api/v1/matrizes/{id}/download` transmite o `.PES` original e envia
  `Content-Disposition` com o nome preservado;
- previews públicos de vitrines usam tokens e não expõem o arquivo `.PES`.

Um desenho sem preview continua aparecendo no catálogo. A ausência de backup no
download retorna uma mensagem de erro própria sem derrubar a aplicação.

## Vitrines públicas

Uma vitrine é criada com pelo menos um desenho. O backend gera token aleatório,
validade de sete dias e snapshots de nome/preview. Apenas vitrines ativas e não
expiradas podem ser consultadas publicamente.

`GET /api/v1/vitrines/{token}/compartilhar` gera a página intermediária com
metadados Open Graph e redirecionamento para o site. `API_PUBLIC_URL` e
`FRONTEND_PUBLIC_URL` precisam corresponder ao ambiente publicado.

## Autenticação

Não há autenticação implementada. As rotas administrativas foram concebidas para
um ambiente privado de uma única usuária. CORS não é autenticação; restrinja a
exposição da API por rede, proxy ou outra camada apropriada ao ambiente.

## Documentação relacionada

- [Desenvolvimento](development.md)
- [Banco e armazenamento](database.md)
- [Segurança](security.md)
- [Testes](testing.md)
