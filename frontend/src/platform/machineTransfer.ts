import type { MachineTransferAdapter } from '@catalogo-bordados/shared'

const unsupported = async (): Promise<never> => {
  throw new Error('O envio para máquina está disponível somente no aplicativo Windows.')
}

export const machineTransferAdapter: MachineTransferAdapter = {
  supported: false,
  listDrives: unsupported,
  writePes: unsupported,
}
