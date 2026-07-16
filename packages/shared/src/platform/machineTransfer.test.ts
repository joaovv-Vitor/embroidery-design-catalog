import { describe, expect, it } from 'vitest'

import { validateRelativeDirectory } from './machineTransfer'

describe('validateRelativeDirectory', () => {
  it('aceita a raiz e subpastas relativas', () => {
    expect(validateRelativeDirectory('')).toBeNull()
    expect(validateRelativeDirectory('Brother/Desenhos')).toBeNull()
    expect(validateRelativeDirectory('Brother\\Desenhos')).toBeNull()
  })

  it.each(['E:/Matrizes', '/Matrizes', '../Matrizes', 'Pasta/../Matrizes'])(
    'rejeita caminho fora da unidade: %s',
    (path) => expect(validateRelativeDirectory(path)).not.toBeNull(),
  )

  it.each(['CON', 'Pasta<1', 'Pasta.', 'Pasta /Interna'])(
    'rejeita nomes inválidos do Windows: %s',
    (path) => expect(validateRelativeDirectory(path)).not.toBeNull(),
  )
})
