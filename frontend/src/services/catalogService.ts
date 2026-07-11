import { api } from './api'
import type { CatalogoResponse, Categoria, DesenhoDetalhe, DesenhoResumo } from '@/types/api'
export const catalogService={
  async list(params:{busca?:string;favorito?:boolean;pagina?:number;por_pagina?:number}){return (await api.get<CatalogoResponse>('/catalogo/desenhos',{params})).data},
  async categories(){return (await api.get<Categoria[]>('/categorias')).data},
  async detail(id:number){return (await api.get<DesenhoDetalhe>(`/desenhos/${id}`)).data},
  async favorite(id:number,favorito:boolean){return (await api.patch<DesenhoResumo>(`/desenhos/${id}/favorito`,{favorito})).data},
  async categorize(id:number,categoria_id:number){return (await api.patch<DesenhoResumo>(`/desenhos/${id}`,{categoria_id})).data}
}
