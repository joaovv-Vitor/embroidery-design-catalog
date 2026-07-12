import { api } from './api'
import type {
  CatalogoResponse,
  Categoria,
  DesenhoDetalhe,
  DesenhoResumo,
  MatrizAtualizada,
} from '@/types/api'

interface CatalogParams {
  busca?: string
  favorito?: boolean
  pagina?: number
  por_pagina?: number
}

interface UpdateDesignData {
  nome?: string
  categoria_id?: number | null
}

interface UpdateMatrixData {
  identificacao_origem?: string | null
  caminho_relativo_origem?: string | null
}

export const catalogService = {
  async list(params: CatalogParams): Promise<CatalogoResponse> {
    return (await api.get<CatalogoResponse>('/catalogo/desenhos', { params })).data
  },

  async categories(): Promise<Categoria[]> {
    return (await api.get<Categoria[]>('/categorias')).data
  },

  async detail(id: number): Promise<DesenhoDetalhe> {
    return (await api.get<DesenhoDetalhe>(`/desenhos/${id}`)).data
  },

  async favorite(id: number, favorito: boolean): Promise<DesenhoResumo> {
    return (await api.patch<DesenhoResumo>(`/desenhos/${id}/favorito`, { favorito })).data
  },

  async updateDesign(id: number, data: UpdateDesignData): Promise<DesenhoResumo> {
    return (await api.patch<DesenhoResumo>(`/desenhos/${id}`, data)).data
  },

  async updateMatrix(id: number, data: UpdateMatrixData): Promise<MatrizAtualizada> {
    return (await api.patch<MatrizAtualizada>(`/matrizes/${id}`, data)).data
  },

  async categorize(id: number, categoria_id: number): Promise<DesenhoResumo> {
    return this.updateDesign(id, { categoria_id })
  },
}
