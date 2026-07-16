export type TransferConflictStrategy = 'ask' | 'replace' | 'rename'

export interface RemovableDrive {
  id: string
  letter: string
  volumeName: string | null
  totalBytes: number
  freeBytes: number
}

export interface WritePesRequest {
  driveId: string
  relativeDirectory: string
  filename: string
  bytes: number[]
  conflictStrategy: TransferConflictStrategy
}

export interface WritePesResult {
  status: 'written' | 'conflict'
  finalPath: string | null
  filename: string
}

export interface MachineTransferAdapter {
  supported: boolean
  listDrives: () => Promise<RemovableDrive[]>
  writePes: (request: WritePesRequest) => Promise<WritePesResult>
}

const WINDOWS_RESERVED_NAMES = /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?$/i
const WINDOWS_INVALID_CHARACTERS = /[<>:"|?*\u0000-\u001f]/

export function validateRelativeDirectory(value: string): string | null {
  const normalized = value.trim().replace(/\\/g, '/')
  if (!normalized) return null
  if (normalized.startsWith('/') || /^[a-z]:/i.test(normalized)) {
    return 'Informe uma pasta relativa dentro da unidade.'
  }

  const segments = normalized.split('/')
  for (const segment of segments) {
    if (!segment || segment === '.' || segment === '..') {
      return 'A pasta informada contém um caminho inválido.'
    }
    if (
      WINDOWS_INVALID_CHARACTERS.test(segment)
      || WINDOWS_RESERVED_NAMES.test(segment)
      || segment.endsWith('.')
      || segment.endsWith(' ')
    ) {
      return `O nome de pasta “${segment}” não é válido no Windows.`
    }
  }
  return null
}
