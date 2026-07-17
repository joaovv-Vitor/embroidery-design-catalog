# Contribuição

O projeto usa um fluxo Git simples, com branches curtas e pull requests. Não é
adotado Git Flow completo.

## Branches

- `main`: versão estável e referência de produção;
- `homolog`: validação integrada antes da produção, quando aplicável;
- `feature/<nome>`: nova funcionalidade;
- `fix/<nome>`: correção comum;
- `hotfix/<nome>`: correção urgente de uma versão estável.

Exemplo:

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/catalogo-progressivo
```

Após o merge, remova a branch temporária local e remota quando ela não for mais
necessária.

## Conventional Commits

Formato obrigatório:

```text
<tipo>(<escopo>): <descrição breve em letras minúsculas>
```

O escopo é recomendado, mas pode ser omitido quando a alteração atinge apenas a
documentação geral.

Tipos usados:

| Tipo | Uso |
|---|---|
| `feat` | Nova funcionalidade. |
| `fix` | Correção de comportamento. |
| `docs` | Documentação. |
| `style` | Formatação sem mudança de lógica. |
| `refactor` | Reestruturação sem alterar comportamento público. |
| `test` | Testes automatizados ou manuais. |
| `chore` | Dependências e manutenção de rotina. |

Escopos sugeridos:

- `db`: modelos e migrations;
- `api`: rotas e schemas;
- `parser`: processamento `.PES` e previews;
- `ui`: site e componentes compartilhados;
- `infra`: Docker, Dokploy e configuração operacional.

Exemplos:

```text
feat(api): adicionar paginação ao catálogo
fix(parser): corrigir orientação do preview
docs: reorganizar documentação do projeto
chore(infra): atualizar imagem do frontend
```

Prefira commits atômicos e títulos curtos. Use corpo e referência à história
quando ajudarem a explicar uma alteração complexa.

## Pull request

Antes de abrir o PR:

- [ ] o escopo está limitado a uma unidade lógica;
- [ ] não há `.env`, segredo, binário gerado ou arquivo temporário versionado;
- [ ] migrations foram revisadas;
- [ ] `npm run check` foi executado quando houver alteração TypeScript/Vue;
- [ ] `pytest` e `ruff check app` foram executados quando houver alteração Python;
- [ ] testes Rust foram executados quando houver alteração Tauri;
- [ ] documentação foi atualizada quando o contrato ou fluxo mudou;
- [ ] testes manuais relevantes foram registrados na descrição.

Use PR para `homolog` quando a mudança exigir validação de deploy. Após homologar,
abra o PR correspondente para `main`. Hotfixes devem ser validados de forma
proporcional ao risco e propagados para as branches mantidas.

## Documentação relacionada

- [Testes](testing.md)
- [Deploy](deployment.md)
- [Arquitetura](architecture.md)
- [Segurança](security.md)
