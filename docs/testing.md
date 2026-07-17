# Testes e validação

## Verificações JavaScript

Na raiz do repositório:

```bash
npm test
npm run typecheck
npm run check
```

`npm run check` executa typecheck dos workspaces, testes do pacote compartilhado e
builds Vite do site e do desktop. Ele não compila a camada Rust nem executa os
testes Python.

## Backend

Com o ambiente virtual ativo:

```bash
cd backend
pytest
ruff check app
```

Para validar integrações reais com o `.env` configurado:

```bash
python scripts/test_connections.py
```

O script de conexões modifica apenas um objeto temporário no bucket e o remove ao
final. Execute-o somente em um ambiente autorizado.

## Tauri/Rust

Em ambiente com Rust e dependências do Tauri:

```bash
cd app/src-tauri
cargo test
cargo clippy -- -D warnings
```

Os comportamentos específicos de unidades removíveis devem ser testados em um
Windows com um dispositivo apropriado conectado.

## Checklist manual

### Catálogo e organização

- [ ] A primeira consulta carrega no máximo 24 desenhos.
- [ ] Pesquisa, categoria, favoritos e ordenação retornam resultados corretos.
- [ ] **Carregar mais desenhos** não duplica cards.
- [ ] Previews são carregados progressivamente e falhas exibem fallback.
- [ ] Detalhes, edição, favorito e download funcionam.
- [ ] O nome original do `.PES` é preservado no download.

### Importação

- [ ] Um `.PES` válido gera desenho, matriz, backup e preview.
- [ ] Extensão inválida apresenta mensagem compreensível.
- [ ] Um lote continua após falha individual.
- [ ] O relatório apresenta processados, importados, rejeitados e motivos.
- [ ] Origem e caminho relativo aparecem nos detalhes quando informados.

### Categorias e lixeira

- [ ] É possível criar, editar e listar categorias.
- [ ] Categoria vinculada não pode ser excluída.
- [ ] Remoção exige confirmação e envia o desenho à lixeira.
- [ ] A lixeira mostra preview, restaura dentro do prazo e exclui definitivamente.

### Vitrines

- [ ] Não é possível criar vitrine sem desenhos.
- [ ] Link público abre sem login enquanto ativo e dentro da validade.
- [ ] Página pública não expõe download, origem, hash, pontos ou cores.
- [ ] Copiar link e compartilhar no WhatsApp usam o domínio correto.
- [ ] Desativação interrompe o acesso e exclusão não remove desenhos.

### Aplicativo Windows

- [ ] Seletor nativo encontra `.pes` e `.PES` recursivamente.
- [ ] Pasta vazia e entradas ilegíveis apresentam estados claros.
- [ ] Nenhum caminho absoluto aparece no catálogo ou em vitrines.
- [ ] **Enviar para máquina** aparece apenas no desktop.
- [ ] Lista de unidades mostra letra, volume e espaço livre.
- [ ] Caminhos absolutos e `..` são rejeitados.
- [ ] Cancelar, substituir e salvar cópia funcionam em conflitos.
- [ ] Remoção da unidade durante a escrita produz erro compreensível.
- [ ] Arquivos temporários não permanecem após falha.

## Homologação antes de produção

- [ ] Migrations aplicadas em uma cópia/ambiente de homologação.
- [ ] Backend e frontend usam URLs do mesmo ambiente.
- [ ] CORS autoriza somente as origens necessárias.
- [ ] Fluxo completo de importação e download validado.
- [ ] Vitrine pública validada em celular ou viewport equivalente.
- [ ] Logs não exibem segredos nem caminhos locais sensíveis.
- [ ] Backup e procedimento de rollback foram confirmados.

## Documentação relacionada

- [Desenvolvimento](development.md)
- [Deploy](deployment.md)
- [Aplicativo desktop](desktop.md)
- [Segurança](security.md)
