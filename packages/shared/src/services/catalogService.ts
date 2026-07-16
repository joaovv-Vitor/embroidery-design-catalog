import axios, { type AxiosInstance } from 'axios'

import type {
  CatalogoResponse,
  Categoria,
  DesenhoDetalhe,
  DesenhoLixeira,
  DesenhoResumo,
  MatrizAtualizada,
} from '../types/api'

export interface CatalogParams { busca?:string; favorito?:boolean; pagina?:number; por_pagina?:number }
export interface UpdateDesignData { nome?:string; categoria_id?:number|null }
export interface UpdateMatrixData { identificacao_origem?:string|null; caminho_relativo_origem?:string|null }
export interface CategoryData { nome:string; cor?:string|null; icone?:string|null }
export interface MatrixDownload { blob:Blob; filename:string }

function downloadEndpoint(downloadUrl: string): string {
  const path = /^https?:\/\//.test(downloadUrl) ? new URL(downloadUrl).pathname : downloadUrl
  return path.replace(/^\/api\/v1/, '')
}

function downloadFilename(contentDisposition: string | undefined): string {
  const encodedFilename = contentDisposition?.match(/filename\*=UTF-8''([^;]+)/i)?.[1]
  return encodedFilename ? decodeURIComponent(encodedFilename) : 'matriz.PES'
}

async function normalizeBlobError(error: unknown): Promise<never> {
  if (axios.isAxiosError(error) && error.response?.data instanceof Blob) {
    try {
      const body = JSON.parse(await error.response.data.text()) as { detail?:string }
      if (body.detail) throw new Error(body.detail)
    } catch (parseError) {
      if (!(parseError instanceof SyntaxError)) throw parseError
    }
  }
  throw error
}

export function createCatalogService(api: AxiosInstance) {
  return {
    async list(params: CatalogParams): Promise<CatalogoResponse> { return (await api.get<CatalogoResponse>('/catalogo/desenhos', { params })).data },
    async categories(): Promise<Categoria[]> { return (await api.get<Categoria[]>('/categorias')).data },
    async createCategory(data: CategoryData): Promise<Categoria> { return (await api.post<Categoria>('/categorias', data)).data },
    async updateCategory(id: number, data: Partial<CategoryData>): Promise<Categoria> { return (await api.patch<Categoria>(`/categorias/${id}`, data)).data },
    async deleteCategory(id: number): Promise<void> { await api.delete(`/categorias/${id}`) },
    async detail(id: number): Promise<DesenhoDetalhe> { return (await api.get<DesenhoDetalhe>(`/desenhos/${id}`)).data },
    async trash(): Promise<DesenhoLixeira[]> { return (await api.get<DesenhoLixeira[]>('/desenhos/lixeira')).data },
    async moveToTrash(id: number): Promise<DesenhoLixeira> { return (await api.delete<DesenhoLixeira>(`/desenhos/${id}`, { data: { confirmar:true } })).data },
    async restoreDesign(id: number): Promise<DesenhoResumo> { return (await api.post<DesenhoResumo>(`/desenhos/${id}/restaurar`)).data },
    async deleteDesignPermanently(id: number): Promise<void> { await api.delete(`/desenhos/${id}/permanente`, { data: { confirmar:true } }) },
    async favorite(id: number, favorito: boolean): Promise<DesenhoResumo> { return (await api.patch<DesenhoResumo>(`/desenhos/${id}/favorito`, { favorito })).data },
    async updateDesign(id: number, data: UpdateDesignData): Promise<DesenhoResumo> { return (await api.patch<DesenhoResumo>(`/desenhos/${id}`, data)).data },
    async updateMatrix(id: number, data: UpdateMatrixData): Promise<MatrizAtualizada> { return (await api.patch<MatrizAtualizada>(`/matrizes/${id}`, data)).data },
    async downloadMatrix(downloadUrl: string): Promise<MatrixDownload> {
      try {
        const response = await api.get<Blob>(downloadEndpoint(downloadUrl), { responseType:'blob' })
        return { blob:response.data, filename:downloadFilename(response.headers['content-disposition']) }
      } catch (error) { return normalizeBlobError(error) }
    },
    async categorize(id: number, categoria_id: number): Promise<DesenhoResumo> {
      return this.updateDesign(id, { categoria_id })
    },
  }
}
