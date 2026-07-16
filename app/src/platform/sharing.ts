import { whatsappShareUrl, type SharingAdapter } from '@catalogo-bordados/shared'

export const sharingAdapter: SharingAdapter = {
  async copyText(value: string): Promise<void> {
    if (!navigator.clipboard?.writeText) {
      throw new Error('A área de transferência não está disponível no aplicativo.')
    }
    await navigator.clipboard.writeText(value)
  },
  shareOnWhatsApp(title: string, link: string): void {
    window.open(whatsappShareUrl(title, link), '_blank', 'noopener,noreferrer')
  },
}
