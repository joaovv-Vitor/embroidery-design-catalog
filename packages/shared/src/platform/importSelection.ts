export interface PesImportCandidate {
  key: string
  name: string
  relativePath: string
  size: number
  lastModified: number
  readFile: () => Promise<File>
}

export interface DirectorySelection {
  folderName: string
  files: PesImportCandidate[]
  unreadableEntries: number
}

export interface ImportSelectionAdapter {
  supportsNativeDirectory: boolean
  fromBrowserFiles: (files: FileList | File[]) => PesImportCandidate[]
  selectDirectory: () => Promise<DirectorySelection | null>
  clearDirectory: () => Promise<void>
}

export function browserPesCandidates(fileList: FileList | File[]): PesImportCandidate[] {
  return Array.from(fileList)
    .filter((file) => file.name.toLowerCase().endsWith('.pes'))
    .map((file) => {
      const relativePath = file.webkitRelativePath || file.name
      return {
        key: `${relativePath}:${file.size}:${file.lastModified}`,
        name: file.name,
        relativePath,
        size: file.size,
        lastModified: file.lastModified,
        readFile: async () => file,
      }
    })
}
