import { createCatalogService } from '@catalogo-bordados/shared'

import { api } from './api'

export const catalogService = createCatalogService(api)
