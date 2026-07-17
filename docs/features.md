# Funcionalidades

Este documento registra somente comportamentos presentes no código atual.

## Implementado

### Catálogo e pesquisa

- cards com preview, nome, categoria e estado de favorito;
- pesquisa por nome do desenho ou nome da categoria;
- filtros por categoria e favoritos;
- ordenação por nome, criação ou atualização;
- paginação de até 50 itens, com 24 itens por padrão e ação de carregar mais;
- lazy loading, skeleton, fallback de imagem e cache HTTP de previews.

### Detalhes e organização

- detalhes do desenho e suas variações de matriz;
- dimensões, pontos, cores, origem e caminho relativo quando disponíveis;
- edição de nome, categoria e dados de origem;
- criação, edição e exclusão segura de categorias;
- marcação e filtro de favoritos.

### Importação e previews

- importação de um arquivo ou de vários `.PES`;
- processamento individual: uma falha não interrompe todo o lote;
- captura de caminhos relativos quando a plataforma fornece essa informação;
- identificação opcional da origem e nome do lote;
- SHA-256, dimensões, pontos, cores e limites extraídos pelo `pyembroidery`;
- preview PNG gerado com Pillow;
- relatório de arquivos importados e rejeitados, com motivo da falha.

### Backup, download e lixeira

- arquivo original armazenado no MinIO com chave interna aleatória;
- nome original mantido no banco e restaurado no download;
- remoção lógica para lixeira, com preview, restauração e prazo configurável;
- exclusão permanente dos registros, preview e backup relacionados.

### Vitrines

- seleção de um ou mais desenhos no catálogo;
- título padrão, nome opcional do cliente e validade padrão de sete dias;
- token público aleatório, sem expor ID sequencial;
- snapshot do nome e preview no momento da criação;
- página pública responsiva, sem download `.PES` ou metadados internos;
- link para copiar ou compartilhar no WhatsApp, com metadados Open Graph;
- listagem, status, desativação e exclusão de vitrines encerradas.

### Aplicativo Windows

- seletor nativo de pasta iniciado pela usuária;
- varredura recursiva de extensões `.pes` sem diferenciar maiúsculas;
- caminhos absolutos mantidos na camada Rust e não enviados ao catálogo;
- leitura isolada de arquivos inacessíveis;
- listagem de unidades reconhecidas pelo Windows como removíveis;
- envio do `.PES` original para raiz ou subpasta relativa;
- validação de espaço, remoção da unidade e nomes inválidos;
- conflito com opções para cancelar, substituir ou criar nome alternativo.

## Limitações conhecidas

- não há autenticação; o ambiente administrativo deve permanecer privado;
- web e desktop exigem conexão com o backend;
- somente o formato `.PES` é processado e enviado à máquina;
- o navegador não faz varredura nativa irrestrita de pastas;
- o envio para máquina funciona apenas no Windows e somente para volumes
  classificados como removíveis;
- dispositivos MTP ou classificados como disco fixo não aparecem nesse fluxo;
- não há atualização automática, operação offline ou sincronização em segundo
  plano;
- o Compose do repositório é de deploy e não cria PostgreSQL ou MinIO localmente.

## Planejado ou em avaliação

Os seguintes itens são possibilidades registradas como limitações atuais e não
estão implementados:

- funcionamento offline;
- atualização automática do aplicativo;
- integração específica com dispositivos MTP ou discos classificados como fixos.

## Documentação relacionada

- [Arquitetura](architecture.md)
- [Desenvolvimento](development.md)
- [Aplicativo desktop](desktop.md)
- [Segurança](security.md)
