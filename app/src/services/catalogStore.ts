import { createCatalogStore } from '@catalogo-bordados/shared'

import { catalogService } from './catalogService'

export const catalogStore = createCatalogStore(catalogService)
