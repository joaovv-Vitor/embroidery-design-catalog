import { describe, expect, it, vi } from 'vitest'

import { createCatalogStore, createLatestRequestGuard } from './catalogStore'

const catalogResponse = {
  itens: [],
  total: 0,
  pagina: 1,
  por_pagina: 24,
  total_paginas: 0,
  tem_mais: false,
}

describe('catalog store', () => {
  it('deduplicates and caches identical catalog requests', async () => {
    const list = vi.fn().mockResolvedValue(catalogResponse)
    const store = createCatalogStore({ list, categories: vi.fn() })

    const [first, second] = await Promise.all([
      store.getCatalog({ busca: 'flor' }),
      store.getCatalog({ busca: ' flor ' }),
    ])
    const third = await store.getCatalog({ busca: 'flor' })

    expect(list).toHaveBeenCalledTimes(1)
    expect(first).toBe(catalogResponse)
    expect(second).toBe(catalogResponse)
    expect(third).toBe(catalogResponse)
  })

  it('uses separate cache entries for distinct filters and invalidates them', async () => {
    const list = vi.fn().mockResolvedValue(catalogResponse)
    const store = createCatalogStore({ list, categories: vi.fn() })

    await store.getCatalog({ categoria_id: 1 })
    await store.getCatalog({ categoria_id: 2 })
    store.invalidateCatalog()
    await store.getCatalog({ categoria_id: 1 })

    expect(list).toHaveBeenCalledTimes(3)
  })

  it('caches categories until they are invalidated', async () => {
    const categories = vi.fn().mockResolvedValue([{ id: 1, nome: 'Flores', cor: null, icone: null, criado_em: '' }])
    const store = createCatalogStore({ list: vi.fn(), categories })

    await store.getCategories()
    await store.getCategories()
    store.invalidateCategories()
    await store.getCategories()

    expect(categories).toHaveBeenCalledTimes(2)
  })

  it('identifies late catalog responses after a newer request starts', () => {
    const guard = createLatestRequestGuard()
    const firstRequest = guard.start()
    const secondRequest = guard.start()

    expect(guard.isCurrent(firstRequest)).toBe(false)
    expect(guard.isCurrent(secondRequest)).toBe(true)
    guard.cancel()
    expect(guard.isCurrent(secondRequest)).toBe(false)
  })
})
