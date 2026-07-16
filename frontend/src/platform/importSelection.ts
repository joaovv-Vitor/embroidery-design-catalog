import {
  browserPesCandidates,
  type ImportSelectionAdapter,
} from '@catalogo-bordados/shared'

export const importSelectionAdapter: ImportSelectionAdapter = {
  supportsNativeDirectory: false,
  fromBrowserFiles: browserPesCandidates,
  async selectDirectory() {
    return null
  },
  async clearDirectory() {},
}
