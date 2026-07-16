export interface SharingAdapter {
  copyText: (value: string) => Promise<void>
  shareOnWhatsApp: (title: string, link: string) => void
}

export function whatsappShareUrl(title: string, link: string): string {
  const message = `Olá! Separei algumas opções de bordado para você: ${title}. Confira aqui: ${link}`
  return `https://wa.me/?text=${encodeURIComponent(message)}`
}
