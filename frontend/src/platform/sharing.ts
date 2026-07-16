import { whatsappShareUrl, type SharingAdapter } from '@catalogo-bordados/shared'

export const sharingAdapter: SharingAdapter = {
  async copyText(value: string): Promise<void> {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(value)
      return
    }

    const input = document.createElement('textarea')
    input.value = value
    input.style.position = 'fixed'
    input.style.opacity = '0'
    document.body.appendChild(input)
    input.select()
    const copied = document.execCommand('copy')
    input.remove()
    if (!copied) throw new Error('Não foi possível copiar o link.')
  },
  shareOnWhatsApp(title: string, link: string): void {
    window.open(whatsappShareUrl(title, link), '_blank', 'noopener,noreferrer')
  },
}
