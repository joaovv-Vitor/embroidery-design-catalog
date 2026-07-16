import { describe, expect, it } from 'vitest'

import { whatsappShareUrl } from './sharing'

describe('whatsappShareUrl', () => {
  it('gera uma URL segura com título e link codificados', () => {
    const result = whatsappShareUrl('Flores & folhas', 'https://catalogo.test/vitrines/token')
    const url = new URL(result)

    expect(url.origin).toBe('https://wa.me')
    expect(url.searchParams.get('text')).toContain('Flores & folhas')
    expect(url.searchParams.get('text')).toContain('https://catalogo.test/vitrines/token')
  })
})
