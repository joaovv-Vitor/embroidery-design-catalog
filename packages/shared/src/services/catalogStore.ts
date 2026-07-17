import type { CatalogParams } from './catalogService'
import type { CatalogoResponse, Categoria } from '../types/api'

export interface CatalogDataSource {
  list: (params: CatalogParams) => Promise<CatalogoResponse>
  categories: () => Promise<Categoria[]>
}

function catalogCacheKey(params: CatalogParams): string {
  return JSON.stringify({
    busca: params.busca?.trim() || undefined,
    categoria_id: params.categoria_id,
    somente_favoritos: params.somente_favoritos || undefined,
    favorito: params.favorito,
    ordenar_por: params.ordenar_por || 'criado_em',
    ordem: params.ordem || 'desc',
    pagina: params.pagina || 1,
    por_pagina: params.por_pagina || 24,
  })
}

export function createLatestRequestGuard() {
  let latestRequest = 0

  return {
    start(): number {
      latestRequest += 1
      return latestRequest
    },
    isCurrent(request: number): boolean {
      return request === latestRequest
    },
    cancel(): void {
      latestRequest += 1
    },
  }
}

export function createCatalogStore(source: CatalogDataSource) {
  const catalogCache = new Map<string, CatalogoResponse>()
  const catalogRequests = new Map<string, Promise<CatalogoResponse>>()
  let categoriesCache: Categoria[] | null = null
  let categoriesRequest: Promise<Categoria[]> | null = null

  async function getCatalog(params: CatalogParams): Promise<CatalogoResponse> {
    const key = catalogCacheKey(params)
    const cached = catalogCache.get(key)
    if (cached) return cached

    const inFlight = catalogRequests.get(key)
    if (inFlight) return inFlight

    const request = source.list(params)
      .then((response) => {
        catalogCache.set(key, response)
        return response
      })
      .finally(() => {
        catalogRequests.delete(key)
      })
    catalogRequests.set(key, request)
    return request
  }

  async function getCategories(): Promise<Categoria[]> {
    if (categoriesCache) return categoriesCache
    if (categoriesRequest) return categoriesRequest

    categoriesRequest = source.categories()
      .then((categories) => {
        categoriesCache = categories
        return categories
      })
      .finally(() => {
        categoriesRequest = null
      })
    return categoriesRequest
  }

  return {
    getCatalog,
    getCategories,
    invalidateCatalog(): void {
      catalogCache.clear()
    },
    invalidateCategories(): void {
      categoriesCache = null
    },
    invalidateAll(): void {
      catalogCache.clear()
      categoriesCache = null
    },
  }
}
