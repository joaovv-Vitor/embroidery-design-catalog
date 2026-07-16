import { invoke } from '@tauri-apps/api/core'
import type {
  MachineTransferAdapter,
  RemovableDrive,
  WritePesRequest,
  WritePesResult,
} from '@catalogo-bordados/shared'

const isTauri = '__TAURI_INTERNALS__' in window

export const machineTransferAdapter: MachineTransferAdapter = {
  supported: isTauri,
  async listDrives(): Promise<RemovableDrive[]> {
    return invoke<RemovableDrive[]>('list_removable_drives')
  },
  async writePes(request: WritePesRequest): Promise<WritePesResult> {
    return invoke<WritePesResult>('write_pes_to_removable_drive', { request })
  },
}
