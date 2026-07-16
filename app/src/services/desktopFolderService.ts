import { invoke } from '@tauri-apps/api/core'

export interface DesktopPesFile {
  id: string
  name: string
  relativePath: string
  size: number
}

export interface DesktopDirectorySelection {
  folderName: string
  files: DesktopPesFile[]
  unreadableEntries: number
}

export function isTauriDesktop(): boolean {
  return '__TAURI_INTERNALS__' in window
}

export const desktopFolderService = {
  async select(): Promise<DesktopDirectorySelection | null> {
    return invoke<DesktopDirectorySelection | null>('select_pes_directory')
  },

  async readFile(file: DesktopPesFile): Promise<File> {
    const bytes = await invoke<number[]>('read_selected_pes_file', { id: file.id })
    return new File([new Uint8Array(bytes)], file.name, {
      type: 'application/octet-stream',
      lastModified: Date.now(),
    })
  },

  async clear(): Promise<void> {
    await invoke('clear_selected_directory')
  },
}

