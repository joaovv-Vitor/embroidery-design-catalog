import type { AxiosInstance } from 'axios'

import type { ImportacaoArquivo, ImportacaoLote } from '../types/api'

export interface SingleImportData { caminho_relativo?:string; identificacao_origem?:string }
export interface BatchImportData { caminhos_relativos:string[]; identificacao_origem?:string; nome_lote?:string }
export type UploadProgressHandler = (progress: number) => void

export function createImportService(api: AxiosInstance) {
  return {
    async single(file: File, data: SingleImportData, onProgress: UploadProgressHandler): Promise<ImportacaoArquivo> {
      const form = new FormData()
      form.append('arquivo', file)
      if (data.caminho_relativo) form.append('caminho_relativo', data.caminho_relativo)
      if (data.identificacao_origem) form.append('identificacao_origem', data.identificacao_origem)
      return (await api.post<ImportacaoArquivo>('/importacoes/arquivo', form, { onUploadProgress:event => onProgress(event.total ? Math.round((event.loaded / event.total) * 100) : 0) })).data
    },
    async batch(files: File[], data: BatchImportData, onProgress: UploadProgressHandler): Promise<ImportacaoLote> {
      const form = new FormData()
      files.forEach((file) => form.append('arquivos', file, file.name))
      form.append('caminhos_relativos', JSON.stringify(data.caminhos_relativos))
      if (data.identificacao_origem) form.append('identificacao_origem', data.identificacao_origem)
      if (data.nome_lote) form.append('nome_lote', data.nome_lote)
      return (await api.post<ImportacaoLote>('/importacoes/lote', form, { onUploadProgress:event => onProgress(event.total ? Math.round((event.loaded / event.total) * 100) : 0) })).data
    },
  }
}
