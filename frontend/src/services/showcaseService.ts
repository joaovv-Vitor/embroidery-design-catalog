import { api } from './api'
import type { VitrineCriada, VitrineGerencial, VitrinePublica } from '@/types/api'

interface CreateShowcaseData {
  desenho_ids: number[]
  titulo?: string
  nome_cliente?: string | null
}

export const showcaseService = {
  async create(data: CreateShowcaseData): Promise<VitrineCriada> {
    return (await api.post<VitrineCriada>('/vitrines', data)).data
  },

  async publicDetail(token: string): Promise<VitrinePublica> {
    return (await api.get<VitrinePublica>(`/vitrines/${encodeURIComponent(token)}`)).data
  },

  async list(): Promise<VitrineGerencial[]> {
    return (await api.get<VitrineGerencial[]>('/vitrines')).data
  },

  async updateStatus(id: number, ativa: boolean): Promise<void> {
    await api.patch(`/vitrines/${id}/status`, { ativa, confirmar: true })
  },

  async deletePermanently(id: number): Promise<void> {
    await api.delete(`/vitrines/${id}`, { data: { confirmar: true } })
  },
}
