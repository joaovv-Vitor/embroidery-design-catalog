import { api } from './api'
import type { ImportacaoArquivo, ImportacaoLote } from '@/types/api'

interface SingleImportData {
  caminho_relativo?: string
  identificacao_origem?: string
}

interface BatchImportData {
  caminhos_relativos: string[]
  identificacao_origem?: string
  nome_lote?: string
}

export const importService = {
  async single(
    file: File,
    data: SingleImportData,
    onProgress: (progress: number) => void,
  ): Promise<ImportacaoArquivo> {
    const form = new FormData()
    form.append('arquivo', file)
    if (data.caminho_relativo) form.append('caminho_relativo', data.caminho_relativo)
    if (data.identificacao_origem) form.append('identificacao_origem', data.identificacao_origem)

    return (
      await api.post<ImportacaoArquivo>('/importacoes/arquivo', form, {
        onUploadProgress: (event) =>
          onProgress(event.total ? Math.round((event.loaded / event.total) * 100) : 0),
      })
    ).data
  },

  async batch(
    files: File[],
    data: BatchImportData,
    onProgress: (progress: number) => void,
  ): Promise<ImportacaoLote> {
    const form = new FormData()
    files.forEach((file) => form.append('arquivos', file, file.name))
    form.append('caminhos_relativos', JSON.stringify(data.caminhos_relativos))
    if (data.identificacao_origem) form.append('identificacao_origem', data.identificacao_origem)
    if (data.nome_lote) form.append('nome_lote', data.nome_lote)

    return (
      await api.post<ImportacaoLote>('/importacoes/lote', form, {
        onUploadProgress: (event) =>
          onProgress(event.total ? Math.round((event.loaded / event.total) * 100) : 0),
      })
    ).data
  },
}
