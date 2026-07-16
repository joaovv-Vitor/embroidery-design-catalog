import { describe, expect, it } from 'vitest'

import { apiErrorMessage } from './apiError'

describe('apiErrorMessage', () => {
  it('preserva mensagens de erro locais', () => {
    expect(apiErrorMessage(new Error('Falha ao ler arquivo'))).toBe('Falha ao ler arquivo')
  })

  it('usa a mensagem alternativa para valores desconhecidos', () => {
    expect(apiErrorMessage(null, 'Operação indisponível')).toBe('Operação indisponível')
  })
})
