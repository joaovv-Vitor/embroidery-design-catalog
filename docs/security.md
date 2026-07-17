# Segurança

## Estado atual

O sistema foi desenvolvido para uma única usuária em ambiente privado e não
implementa login ou autorização. As rotas administrativas não devem ser tratadas
como uma API pública irrestrita.

CORS controla quais páginas podem ler respostas no navegador, mas não impede
chamadas feitas por outros clientes HTTP. Use isolamento de rede, proxy, firewall
ou outra camada compatível com o ambiente para proteger a administração.

## Segredos e variáveis

- mantenha `.env` e `.env.local` fora do Git;
- versione apenas `.env.example` com valores fictícios;
- armazene credenciais de banco e MinIO no gerenciador de variáveis do ambiente;
- não coloque segredos em `VITE_*`: variáveis Vite são incorporadas ao frontend;
- faça rotação de credenciais após qualquer exposição;
- não registre tokens, senhas, URLs assinadas ou corpos de arquivos em logs.

`VITE_API_URL`, `API_PUBLIC_URL` e `FRONTEND_PUBLIC_URL` são URLs públicas, não
segredos, mas devem corresponder ao ambiente correto para evitar compartilhamento
de links inválidos.

## CORS

`CORS_ALLOWED_ORIGINS` usa uma lista JSON explícita. Autorize somente o site, os
endereços locais necessários no desenvolvimento e a origem do WebView desktop
quando aplicável. Evite curingas, principalmente porque a API permite credenciais
no middleware CORS.

## PostgreSQL e MinIO

- não exponha PostgreSQL ou o console MinIO diretamente à internet sem necessidade;
- use credenciais distintas por ambiente e com o menor privilégio viável;
- aplique TLS nos endpoints públicos;
- mantenha o bucket privado; previews e downloads são entregues pela API;
- preserve o nome original apenas nos metadados, usando chaves aleatórias no bucket;
- verifique backups e restauração periodicamente.

## Vitrines públicas

Vitrines usam tokens aleatórios e snapshots. A resposta pública deve apresentar
somente título, cliente opcional, número, nome e preview das opções.

Ela não deve expor:

- download ou conteúdo do `.PES`;
- hash, tamanho do arquivo ou chave do storage;
- pontos, cores, origem, pendrive ou caminho interno;
- IDs sequenciais usados pela administração.

Desativação e expiração devem interromper o acesso. O token é um segredo de
compartilhamento: quem possui o link pode visualizar a vitrine enquanto válida.

## Aplicativo Tauri

O site não recebe permissões nativas. No desktop:

- o seletor é aberto por ação explícita da usuária;
- caminhos absolutos permanecem na camada Rust;
- links simbólicos não são seguidos na varredura;
- leituras são limitadas aos IDs da seleção atual;
- destinos de escrita são unidades removíveis registradas na sessão;
- nomes e subpastas passam por validação contra travessia e regras do Windows;
- o dispositivo e seu serial são verificados novamente antes da escrita.

Não adicione permissões gerais de filesystem ou shell sem necessidade e revisão
específica. Comandos Tauri devem validar toda entrada recebida do Vue.

## Backup e resposta a incidentes

Mantenha backups coordenados do PostgreSQL e do bucket. Um procedimento mínimo:

1. definir frequência e retenção;
2. proteger e, quando possível, criptografar as cópias;
3. testar restauração em ambiente separado;
4. registrar a versão da aplicação e migrations compatíveis;
5. em incidente, interromper escritas, preservar logs e trocar credenciais
   potencialmente comprometidas.

Não existe automação de backup/restauração no repositório atual.

## Documentação relacionada

- [Arquitetura](architecture.md)
- [Banco e armazenamento](database.md)
- [Deploy](deployment.md)
- [Aplicativo desktop](desktop.md)
