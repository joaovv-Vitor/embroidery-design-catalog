import { invoke } from '@tauri-apps/api/core'
import {
  browserPesCandidates,
  type DirectorySelection,
  type ImportSelectionAdapter,
  type PesImportCandidate,
} from '@catalogo-bordados/shared'

interface NativePesFile {
  id: string
  name: string
  relativePath: string
  size: number
}

interface NativeDirectorySelection {
  folderName: string
  files: NativePesFile[]
  unreadableEntries: number
}

async function readNativeFile(file: NativePesFile): Promise<File> {
  const bytes = await invoke<number[]>('read_selected_pes_file', { id: file.id })
  return new File([new Uint8Array(bytes)], file.name, {
    type: 'application/octet-stream',
    lastModified: Date.now(),
  })
}

function nativeCandidate(file: NativePesFile): PesImportCandidate {
  return {
    key: `native:${file.id}`,
    name: file.name,
    relativePath: file.relativePath,
    size: file.size,
    lastModified: 0,
    readFile: () => readNativeFile(file),
  }
}

export const importSelectionAdapter: ImportSelectionAdapter = {
  supportsNativeDirectory: '__TAURI_INTERNALS__' in window,
  fromBrowserFiles: browserPesCandidates,
  async selectDirectory(): Promise<DirectorySelection | null> {
    const selection = await invoke<NativeDirectorySelection | null>('select_pes_directory')
    if (!selection) return null
    return {
      folderName: selection.folderName,
      files: selection.files.map(nativeCandidate),
      unreadableEntries: selection.unreadableEntries,
    }
  },
  async clearDirectory(): Promise<void> {
    await invoke('clear_selected_directory')
  },
}
