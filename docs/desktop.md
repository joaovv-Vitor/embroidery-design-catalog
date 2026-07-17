# Aplicativo desktop Windows

O aplicativo desktop reutiliza a interface Vue do catálogo e adiciona somente os
recursos que exigem integração nativa. As regras de importação, processamento e
persistência continuam no backend.

## Execução em desenvolvimento

Pré-requisitos:

- Windows 10 ou 11;
- Node.js e dependências instaladas na raiz do monorepo;
- Rust stable com target MSVC;
- Microsoft C++ Build Tools e WebView2, conforme os requisitos do Tauri v2;
- `app/.env.local` com `VITE_API_URL`.

Na raiz do repositório:

```powershell
npm run dev:app
```

O Tauri inicia o Vite em `http://localhost:5173`. O watcher ignora
`app/src-tauri/target` para não observar executáveis temporários do Cargo no
Windows.

## Gerar instaladores

```powershell
npm install
npm run build:app
```

O projeto gera bundles `nsis` e `msi` em:

```text
app/src-tauri/target/release/bundle/
```

O instalador NSIS usa o modo `currentUser`. A URL da API vem de `VITE_API_URL` no
momento do build.

## Importação de pastas

Ao selecionar uma pasta, a camada Rust:

1. abre o seletor nativo após ação da usuária;
2. canonicaliza a pasta escolhida;
3. percorre subpastas sem seguir links simbólicos;
4. aceita somente `.pes`, sem diferenciar maiúsculas e minúsculas;
5. ignora entradas inacessíveis sem cancelar toda a seleção;
6. envia ao Vue identificadores, nomes, tamanhos e caminhos relativos.

Os caminhos absolutos ficam em memória na camada Rust. A leitura posterior só é
permitida para IDs pertencentes à seleção atual, que pode ser limpa pela usuária.

## Envio para a máquina

No escopo atual, a máquina é tratada como uma unidade removível do Windows. O
aplicativo lista letra, nome do volume, capacidade e espaço livre quando essas
informações estão disponíveis.

O fluxo baixa o backup `.PES` pela API e permite gravá-lo na raiz ou em uma
subpasta relativa. Antes da escrita, o Rust valida:

- se o volume continua sendo o mesmo dispositivo removível selecionado;
- se o nome recebido termina em `.PES` e é válido no Windows;
- se a pasta não é absoluta e não contém travessia com `..`;
- se existe espaço livre suficiente.

A gravação usa arquivo temporário e sincronização em disco. Em conflito, a
usuária pode cancelar, substituir preservando o anterior em caso de falha, ou
salvar como `nome (1).PES`.

Dispositivos MTP ou classificados pelo Windows como disco fixo não são listados.
O aplicativo não inicia o bordado e não usa protocolo proprietário da máquina.

## Permissões e isolamento

A capability da janela principal concede apenas `core:default`. Operações de
arquivo são comandos Rust próprios, com validação de caminho e estado interno; o
site web não recebe essas permissões.

O aplicativo precisa acessar a API configurada. Em desenvolvimento, autorize a
origem local do Vite no CORS. Para o aplicativo instalado, inclua a origem do
WebView Tauri usada pelo ambiente. CORS limita chamadas do navegador, mas não
substitui autenticação ou isolamento de rede.

## Limitações

- requer conexão com o backend;
- não funciona offline e não possui atualização automática;
- não monitora pastas ou pendrives em segundo plano;
- a página pública de vitrine permanece no site;
- o build do instalador Windows deve ser feito em ambiente Windows compatível.

## Documentação relacionada

- [Desenvolvimento](development.md)
- [Funcionalidades](features.md)
- [Arquitetura](architecture.md)
- [Segurança](security.md)
- [Testes](testing.md)
