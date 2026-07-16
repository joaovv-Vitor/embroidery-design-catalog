import { describe, expect, it } from 'vitest'

import { browserPesCandidates } from './importSelection'

function fileStub(name: string, relativePath = ''): File {
  return {
    name,
    size: 128,
    lastModified: 1234,
    webkitRelativePath: relativePath,
  } as File
}

describe('browserPesCandidates', () => {
  it('aceita arquivos PES sem diferenciar maiúsculas e minúsculas', () => {
    const files = [fileStub('flor.PES'), fileStub('folha.pes'), fileStub('foto.png')]

    const candidates = browserPesCandidates(files)

    expect(candidates.map(({ name }) => name)).toEqual(['flor.PES', 'folha.pes'])
  })

  it('preserva caminho relativo e devolve o arquivo selecionado', async () => {
    const file = fileStub('rosa.pes', 'flores/rosa.pes')

    const [candidate] = browserPesCandidates([file])

    expect(candidate.relativePath).toBe('flores/rosa.pes')
    await expect(candidate.readFile()).resolves.toBe(file)
  })
})
