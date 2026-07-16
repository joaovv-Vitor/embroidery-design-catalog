<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  AlertCircle,
  CheckCircle2,
  FileCheck2,
  FileX2,
  FolderOpen,
  RotateCcw,
  Trash2,
  UploadCloud,
} from 'lucide-vue-next'

import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import { apiErrorMessage } from '@/composables/useApiError'
import { importSelectionAdapter } from '@/platform/importSelection'
import { importService } from '@/services/importService'
import type { ImportacaoLote } from '@/types/api'
import type { PesImportCandidate } from '@catalogo-bordados/shared'

const router = useRouter()
const selectedFiles = ref<PesImportCandidate[]>([])
const origin = ref('')
const batchName = ref('')
const dragging = ref(false)
const sending = ref(false)
const uploadProgress = ref(0)
const report = ref<ImportacaoLote | null>(null)
const error = ref('')
const ignoredFiles = ref(0)

const totalSize = computed(() =>
  selectedFiles.value.reduce((total, selected) => total + selected.size, 0),
)

const hasRelativePaths = computed(() =>
  selectedFiles.value.some((selected) => selected.relativePath !== selected.name),
)

function addFiles(fileList: FileList | File[]): void {
  error.value = ''
  report.value = null

  const files = Array.from(fileList)
  const candidates = importSelectionAdapter.fromBrowserFiles(files)
  ignoredFiles.value += files.length - candidates.length
  const existingKeys = new Set(selectedFiles.value.map(({ key }) => key))
  for (const candidate of candidates) {
    if (existingKeys.has(candidate.key)) continue
    existingKeys.add(candidate.key)
    selectedFiles.value.push(candidate)
  }

  if (!candidates.length && files.length) {
    error.value = 'Nenhum arquivo .PES foi encontrado na seleção.'
  }
}

function handleInput(event: Event): void {
  const input = event.target as HTMLInputElement
  if (input.files) addFiles(input.files)
  input.value = ''
}

function handleDrop(event: DragEvent): void {
  dragging.value = false
  if (event.dataTransfer?.files) addFiles(event.dataTransfer.files)
}

function removeFile(index: number): void {
  selectedFiles.value.splice(index, 1)
}

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

async function submit(): Promise<void> {
  if (!selectedFiles.value.length) return

  sending.value = true
  error.value = ''
  uploadProgress.value = 0

  try {
    report.value = await importService.batch(
      await Promise.all(selectedFiles.value.map(({ readFile }) => readFile())),
      {
        caminhos_relativos: selectedFiles.value.map(({ relativePath }) => relativePath),
        identificacao_origem: origin.value.trim() || undefined,
        nome_lote: batchName.value.trim() || undefined,
      },
      (progress) => {
        uploadProgress.value = progress
      },
    )
  } catch (requestError) {
    error.value = apiErrorMessage(requestError, 'Não foi possível importar este lote.')
  } finally {
    sending.value = false
  }
}

function reset(): void {
  selectedFiles.value = []
  origin.value = ''
  batchName.value = ''
  uploadProgress.value = 0
  report.value = null
  error.value = ''
  ignoredFiles.value = 0
}
</script>

<template>
  <section class="mx-auto max-w-5xl">
    <h1 class="font-serif text-4xl text-purple md:text-5xl">Importar matrizes</h1>
    <p class="mt-2 text-muted">
      Selecione uma pasta, vários arquivos ou arraste suas matrizes .PES para cadastrar o acervo.
    </p>

    <div v-if="report" class="mt-9 space-y-6">
      <div class="rounded-3xl border border-line bg-white p-6 shadow-soft sm:p-8">
        <div class="flex flex-col justify-between gap-5 sm:flex-row sm:items-center">
          <div>
            <CheckCircle2 class="text-sage" :size="44" />
            <h2 class="mt-3 font-serif text-3xl text-purple">Importação concluída</h2>
            <p class="mt-1 text-muted">{{ report.nome_lote }}</p>
          </div>
          <div class="grid grid-cols-3 gap-3 text-center">
            <div class="rounded-2xl bg-cream px-4 py-3">
              <strong class="block text-2xl text-purple">{{ report.total_arquivos }}</strong>
              <span class="text-xs text-muted">processados</span>
            </div>
            <div class="rounded-2xl bg-green-50 px-4 py-3">
              <strong class="block text-2xl text-green-700">{{ report.arquivos_importados }}</strong>
              <span class="text-xs text-green-700">importados</span>
            </div>
            <div class="rounded-2xl bg-red-50 px-4 py-3">
              <strong class="block text-2xl text-red-700">{{ report.arquivos_com_falha }}</strong>
              <span class="text-xs text-red-700">rejeitados</span>
            </div>
          </div>
        </div>

        <div class="mt-7 max-h-[420px] space-y-2 overflow-y-auto pr-1">
          <article
            v-for="item in report.itens"
            :key="item.id"
            class="flex items-start gap-3 rounded-xl border border-line p-3"
          >
            <FileCheck2 v-if="item.status === 'importado'" class="shrink-0 text-sage" :size="20" />
            <FileX2 v-else class="shrink-0 text-red-600" :size="20" />
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-ink">{{ item.nome_arquivo }}</p>
              <p v-if="item.caminho_relativo" class="truncate text-xs text-muted">
                {{ item.caminho_relativo }}
              </p>
              <p v-if="item.motivo_falha" class="mt-1 text-xs text-red-700">
                {{ item.motivo_falha }}
              </p>
            </div>
            <span
              :class="[
                'rounded-full px-2 py-1 text-xs font-semibold',
                item.status === 'importado'
                  ? 'bg-green-50 text-green-700'
                  : 'bg-red-50 text-red-700',
              ]"
            >
              {{ item.status === 'importado' ? 'Importado' : 'Falha' }}
            </span>
          </article>
        </div>

        <div class="mt-7 flex flex-wrap gap-3">
          <button class="primary-button" @click="router.push('/')">Ver no catálogo</button>
          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-xl border border-line px-5 py-3 font-semibold text-purple"
            @click="reset"
          >
            <RotateCcw :size="18" />
            Importar outro lote
          </button>
        </div>
      </div>
    </div>

    <form
      v-else
      class="mt-9 rounded-3xl border border-line bg-white p-5 shadow-sm md:p-8"
      @submit.prevent="submit"
    >
      <div
        :class="[
          'flex min-h-64 flex-col items-center justify-center rounded-2xl border-2 border-dashed p-6 text-center transition',
          dragging ? 'border-terracotta bg-[#FFF7F3]' : 'border-line bg-cream',
        ]"
        @dragover.prevent="dragging = true"
        @dragleave.prevent="dragging = false"
        @drop.prevent="handleDrop"
      >
        <UploadCloud :size="48" class="text-terracotta" />
        <strong class="mt-4 text-lg text-purple">Arraste seus arquivos .PES aqui</strong>
        <span class="mt-1 text-sm text-muted">ou escolha arquivos e pastas no computador</span>

        <div class="mt-6 flex flex-wrap justify-center gap-3">
          <label class="primary-button cursor-pointer">
            <FileCheck2 :size="18" />
            Selecionar arquivos
            <input
              class="sr-only"
              type="file"
              accept=".pes,.PES"
              multiple
              :disabled="sending"
              @change="handleInput"
            />
          </label>
          <label
            class="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-line bg-white px-5 py-3 font-semibold text-purple"
          >
            <FolderOpen :size="18" />
            Selecionar pasta
            <input
              class="sr-only"
              type="file"
              accept=".pes,.PES"
              multiple
              webkitdirectory
              :disabled="sending"
              @change="handleInput"
            />
          </label>
        </div>
      </div>

      <div v-if="selectedFiles.length" class="mt-6 rounded-2xl border border-line">
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-line p-4">
          <div>
            <strong class="text-purple">
              {{ selectedFiles.length }} {{ selectedFiles.length === 1 ? 'arquivo selecionado' : 'arquivos selecionados' }}
            </strong>
            <p class="mt-0.5 text-xs text-muted">
              {{ formatSize(totalSize) }}
              <span v-if="hasRelativePaths"> · caminhos da pasta capturados</span>
            </p>
          </div>
          <button
            type="button"
            class="text-sm font-medium text-red-600"
            @click="selectedFiles = []"
          >
            Limpar lista
          </button>
        </div>

        <div class="max-h-72 divide-y divide-line overflow-y-auto">
          <div
            v-for="(selected, index) in selectedFiles"
            :key="selected.key"
            class="flex items-center gap-3 p-3"
          >
            <FileCheck2 class="shrink-0 text-sage" :size="19" />
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium">{{ selected.name }}</p>
              <p class="truncate text-xs text-muted">
                {{ selected.relativePath }} · {{ formatSize(selected.size) }}
              </p>
            </div>
            <button
              type="button"
              class="rounded-lg p-2 text-muted hover:bg-red-50 hover:text-red-600"
              :aria-label="`Remover ${selected.name}`"
              @click="removeFile(index)"
            >
              <Trash2 :size="17" />
            </button>
          </div>
        </div>
      </div>

      <p v-if="ignoredFiles" class="mt-3 text-xs text-muted">
        {{ ignoredFiles }} {{ ignoredFiles === 1 ? 'arquivo foi ignorado' : 'arquivos foram ignorados' }} por não possuir formato .PES.
      </p>

      <div class="mt-7 grid gap-5 md:grid-cols-2">
        <label class="text-sm font-medium text-purple">
          Nome do lote <span class="font-normal text-muted">(opcional)</span>
          <input
            v-model="batchName"
            class="field mt-2"
            maxlength="255"
            placeholder="Ex.: Matrizes de flores"
            :disabled="sending"
          />
        </label>
        <label class="text-sm font-medium text-purple">
          Identificação da origem <span class="font-normal text-muted">(opcional)</span>
          <input
            v-model="origin"
            class="field mt-2"
            maxlength="255"
            placeholder="Ex.: Pendrive Azul ou Acervo antigo"
            :disabled="sending"
          />
        </label>
      </div>

      <div
        v-if="error"
        class="mt-5 flex items-start gap-2 rounded-xl bg-red-50 p-4 text-sm text-red-700"
        role="alert"
      >
        <AlertCircle :size="19" class="shrink-0" />
        {{ error }}
      </div>

      <div v-if="sending" class="mt-6" aria-live="polite">
        <div class="mb-2 flex justify-between text-sm text-muted">
          <span>
            {{ uploadProgress < 100 ? 'Enviando arquivos…' : 'Processando matrizes e gerando previews…' }}
          </span>
          <span>{{ uploadProgress }}%</span>
        </div>
        <div class="h-2 overflow-hidden rounded-full bg-line">
          <div
            class="h-full bg-terracotta transition-all"
            :style="{ width: `${Math.max(uploadProgress, 5)}%` }"
          ></div>
        </div>
        <p class="mt-2 text-xs text-muted">Cada arquivo é processado separadamente. Uma falha não interrompe o lote.</p>
      </div>

      <div class="mt-7 flex flex-wrap items-center gap-3">
        <button class="primary-button" :disabled="!selectedFiles.length || sending">
          <LoadingSpinner v-if="sending" />
          <UploadCloud v-else :size="19" />
          {{ sending ? 'Processando lote…' : `Importar ${selectedFiles.length || ''} matrizes` }}
        </button>
      </div>
    </form>
  </section>
</template>
