export interface CategoriaDetalhe { id:number; nome:string; cor:string|null; icone:string|null }
export interface Categoria extends CategoriaDetalhe { criado_em:string }
export interface DesenhoCard { id:number; nome:string; favorito:boolean; categoria:CategoriaDetalhe|null; preview_url:string|null }
export interface CatalogoResponse { itens:DesenhoCard[]; total:number; pagina:number; por_pagina:number; total_paginas:number; tem_mais:boolean }
export interface MatrizVariacao { id:number; formato:string; rotulo_tamanho:string|null; largura_mm:number; altura_mm:number; quantidade_cores:number; quantidade_pontos:number; origem_identificacao:string|null; caminho_relativo_origem:string|null; download_url:string }
export interface MatrizAtualizada { id:number; origem_importacao_id:number|null; identificacao_origem:string|null; caminho_relativo_origem:string|null }
export interface DesenhoDetalhe extends DesenhoCard { categoria_id:number|null; descricao:string|null; matrizes:MatrizVariacao[] }
export interface DesenhoResumo { id:number; nome:string; categoria_id:number|null; favorito:boolean }
export interface DesenhoLixeira { id:number; nome:string; preview_url:string|null; excluido_em:string; recuperavel_ate:string; aviso:string }
export interface ImportacaoArquivo { importacao_id:number; item_importacao_id:number; desenho_id:number; matriz_id:number; nome:string; largura_mm:number; altura_mm:number; quantidade_pontos:number; quantidade_cores:number }
export interface ItemImportacaoLote { id:number; nome_arquivo:string; caminho_relativo:string|null; status:string; matriz_id:number|null; motivo_falha:string|null }
export interface ImportacaoLote { id:number; nome_lote:string; status:string; total_arquivos:number; arquivos_importados:number; arquivos_com_falha:number; iniciado_em:string; finalizado_em:string|null; itens:ItemImportacaoLote[] }
export interface ApiErrorBody { detail?: string | Array<{msg:string}> }

export interface ItemVitrineCriada { id:number; desenho_id:number|null; nome:string; preview_url:string|null }
export interface VitrineCriada { token:string; titulo:string; nome_cliente:string|null; criado_em:string; expira_em:string; quantidade_desenhos:number; itens:ItemVitrineCriada[]; link_publico:string }
export interface ItemVitrinePublica { numero:number; nome:string; preview_url:string|null }
export interface VitrinePublica { titulo:string; nome_cliente:string|null; expira_em:string; quantidade_desenhos:number; itens:ItemVitrinePublica[] }
export type StatusVitrine = 'ativa'|'expirada'|'desativada'
export interface VitrineGerencial { id:number; titulo:string; quantidade_desenhos:number; criado_em:string; expira_em:string; status:StatusVitrine; link_publico:string|null }
