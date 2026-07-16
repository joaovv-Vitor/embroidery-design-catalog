<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import {
  AlertCircle,
  CheckCircle2,
  HardDrive,
  RefreshCw,
  Send,
  X,
} from 'lucide-vue-next'

import {
  apiErrorMessage,
  type MatrizVariacao,
  type RemovableDrive,
  type TransferConflictStrategy,
  type WritePesRequest,
  validateRelativeDirectory,
} from '@catalogo-bordados/shared'
import { machineTransferAdapter } from '@catalogo-runtime/platform/machineTransfer'
import { catalogService } from '@catalogo-runtime/services/catalogService'

import LoadingSpinner from '../ui/LoadingSpinner.vue'

const props = defineProps<{
  designName: string
  matrix: MatrizVariacao
}>()

const emit = defineEmits<{ close: [] }>()

const drives = ref<RemovableDrive[]>([])
const selectedDriveId = ref('')
const relativeDirectory = ref('')
const loadingDrives = ref(false)
const phase = ref<'idle' | 'downloading' | 'writing'>('idle')
const error = ref('')
const conflict = ref(false)
const finalPath = ref('')
const pendingRequest = shallowRef<WritePesRequest | null>(null)
let previousBodyOverflow = ''

const busy = computed(() => phase.value !== 'idle')
const selectedDrive = computed(() =>
  drives.value.find((drive) => drive.id === selectedDriveId.value) ?? null,
)
const directoryError = computed(() => validateRelativeDirectory(relativeDirectory.value))
const destinationPreview = computed(() => {
  if (!selectedDrive.value) return 'Selecione uma unidade'
  const directory = relativeDirectory.value.trim().replace(/\\/g, '/').replace(/^\/+|\/+$/g, '')
  return directory
    ? `${selectedDrive.value.letter}\\${directory.replace(/\//g, '\\')}`
    : `${selectedDrive.value.letter}\\`
})

function formatBytes(bytes: number): string {
  if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1)} MB livres`
  return `${(bytes / 1024 ** 3).toFixed(1)} GB livres`
}

function close(): void {
  if (!busy.value) emit('close')
}

function closeOnEscape(event: KeyboardEvent): void {
  if (event.key === 'Escape') close()
}

async function loadDrives(): Promise<void> {
  loadingDrives.value = true
  error.value = ''
  conflict.value = false
  pendingRequest.value = null
  try {
    drives.value = await machineTransferAdapter.listDrives()
    if (!drives.value.some((drive) => drive.id === selectedDriveId.value)) {
      selectedDriveId.value = drives.value.length === 1 ? drives.value[0].id : ''
    }
  } catch (loadError) {
    drives.value = []
    selectedDriveId.value = ''
    error.value = apiErrorMessage(loadError, 'Não foi possível consultar as unidades removíveis.')
  } finally {
    loadingDrives.value = false
  }
}

async function prepareRequest(): Promise<WritePesRequest> {
  phase.value = 'downloading'
  const download = await catalogService.downloadMatrix(props.matrix.download_url)
  const bytes = Array.from(new Uint8Array(await download.blob.arrayBuffer()))
  return {
    driveId: selectedDriveId.value,
    relativeDirectory: relativeDirectory.value.trim(),
    filename: download.filename,
    bytes,
    conflictStrategy: 'ask',
  }
}

async function send(strategy: TransferConflictStrategy = 'ask'): Promise<void> {
  if (!selectedDrive.value || directoryError.value || busy.value) return

  error.value = ''
  finalPath.value = ''
  try {
    const request = pendingRequest.value ?? await prepareRequest()
    pendingRequest.value = request
    phase.value = 'writing'
    const result = await machineTransferAdapter.writePes({
      ...request,
      driveId: selectedDriveId.value,
      relativeDirectory: relativeDirectory.value.trim(),
      conflictStrategy: strategy,
    })
    if (result.status === 'conflict') {
      conflict.value = true
      return
    }

    conflict.value = false
    pendingRequest.value = null
    finalPath.value = result.finalPath ?? result.filename
  } catch (sendError) {
    error.value = apiErrorMessage(sendError, 'Não foi possível enviar a matriz para a unidade.')
  } finally {
    phase.value = 'idle'
  }
}

watch([selectedDriveId, relativeDirectory], () => {
  if (busy.value) return
  conflict.value = false
  pendingRequest.value = null
  finalPath.value = ''
})

onMounted(() => {
  previousBodyOverflow = document.body.style.overflow
  document.body.style.overflow = 'hidden'
  window.addEventListener('keydown', closeOnEscape)
  void loadDrives()
})

onBeforeUnmount(() => {
  document.body.style.overflow = previousBodyOverflow
  window.removeEventListener('keydown', closeOnEscape)
})
</script>

<template>
  <div
    class="fixed inset-0 z-[90] flex items-center justify-center bg-ink/70 p-4 backdrop-blur-sm"
    role="dialog"
    aria-modal="true"
    aria-labelledby="machine-transfer-title"
    @click.self="close"
  >
    <div class="max-h-[94vh] w-full max-w-2xl overflow-y-auto rounded-3xl bg-white p-6 shadow-2xl sm:p-8">
      <header class="flex items-start justify-between gap-4">
        <div>
          <span class="inline-flex rounded-2xl bg-purple/10 p-3 text-purple">
            <HardDrive :size="28" />
          </span>
          <h2 id="machine-transfer-title" class="mt-4 font-serif text-3xl text-purple">
            Enviar para máquina
          </h2>
          <p class="mt-1 text-sm text-muted">Escolha manualmente a unidade conectada.</p>
        </div>
        <button
          type="button"
          class="rounded-full border border-line p-2 text-muted"
          aria-label="Fechar envio para máquina"
          :disabled="busy"
          @click="close"
        >
          <X />
        </button>
      </header>

      <div v-if="finalPath" class="mt-6 rounded-2xl bg-green-50 p-5 text-green-800" role="status">
        <div class="flex items-start gap-3">
          <CheckCircle2 :size="24" class="shrink-0" />
          <div class="min-w-0">
            <strong class="block">Matriz enviada com sucesso.</strong>
            <p class="mt-1 break-all font-mono text-sm">{{ finalPath }}</p>
          </div>
        </div>
        <button type="button" class="primary-button mt-5" @click="emit('close')">Concluir</button>
      </div>

      <template v-else>
        <section class="mt-7">
          <div class="flex items-center justify-between gap-3">
            <label for="machine-drive" class="text-sm font-semibold text-purple">Unidade de destino</label>
            <button
              type="button"
              class="inline-flex items-center gap-2 text-sm font-medium text-purple disabled:opacity-50"
              :disabled="loadingDrives || busy"
              @click="loadDrives"
            >
              <RefreshCw :size="16" :class="loadingDrives ? 'animate-spin' : ''" />
              Atualizar dispositivos
            </button>
          </div>

          <select
            id="machine-drive"
            v-model="selectedDriveId"
            class="field mt-2"
            :disabled="loadingDrives || busy || !drives.length"
          >
            <option value="">Selecione uma unidade removível</option>
            <option v-for="drive in drives" :key="drive.id" :value="drive.id">
              {{ drive.letter }} — {{ drive.volumeName || 'Unidade removível' }} — {{ formatBytes(drive.freeBytes) }}
            </option>
          </select>

          <p v-if="!loadingDrives && !drives.length && !error" class="mt-3 rounded-xl bg-amber-50 p-4 text-sm text-amber-800">
            Nenhuma unidade removível foi encontrada. Conecte a máquina e atualize a lista.
          </p>
        </section>

        <label class="mt-6 block text-sm font-semibold text-purple">
          Pasta dentro da unidade <span class="font-normal text-muted">(opcional)</span>
          <input
            v-model="relativeDirectory"
            class="field mt-2"
            placeholder="Ex.: Brother/Desenhos"
            :disabled="busy"
          />
        </label>
        <p v-if="directoryError" class="mt-2 text-sm text-red-700">{{ directoryError }}</p>
        <p v-else class="mt-2 text-xs text-muted">A raiz da unidade será usada quando o campo estiver vazio.</p>

        <section class="mt-6 rounded-2xl border border-line bg-cream p-5">
          <h3 class="font-semibold text-purple">Confirme o envio</h3>
          <dl class="mt-3 grid gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt class="text-muted">Desenho</dt>
              <dd class="font-medium text-ink">{{ designName }}</dd>
            </div>
            <div>
              <dt class="text-muted">Variação</dt>
              <dd class="font-medium text-ink">{{ matrix.rotulo_tamanho || matrix.formato }}</dd>
            </div>
            <div>
              <dt class="text-muted">Formato</dt>
              <dd class="font-medium uppercase text-ink">{{ matrix.formato }}</dd>
            </div>
            <div>
              <dt class="text-muted">Destino</dt>
              <dd class="break-all font-mono font-medium text-ink">{{ destinationPreview }}</dd>
            </div>
          </dl>
        </section>

        <div v-if="conflict" class="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-5">
          <strong class="text-amber-900">Já existe um arquivo com esse nome no destino.</strong>
          <p class="mt-1 text-sm text-amber-800">Escolha como deseja continuar.</p>
          <div class="mt-4 flex flex-wrap gap-3">
            <button type="button" class="rounded-xl bg-red-600 px-4 py-2 font-semibold text-white" @click="send('replace')">
              Substituir
            </button>
            <button type="button" class="rounded-xl border border-line bg-white px-4 py-2 font-semibold text-purple" @click="send('rename')">
              Salvar uma cópia
            </button>
            <button type="button" class="px-3 py-2 font-semibold text-muted" @click="emit('close')">Cancelar</button>
          </div>
        </div>

        <div v-if="error" class="mt-5 flex gap-2 rounded-xl bg-red-50 p-4 text-sm text-red-700" role="alert">
          <AlertCircle :size="19" class="shrink-0" />
          {{ error }}
        </div>

        <div v-if="busy" class="mt-5 rounded-xl bg-purple/5 p-4 text-sm text-purple" aria-live="polite">
          <div class="flex items-center gap-3">
            <LoadingSpinner />
            {{ phase === 'downloading' ? 'Baixando o arquivo original…' : 'Copiando para a unidade selecionada…' }}
          </div>
        </div>

        <footer v-if="!conflict" class="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            class="rounded-xl border border-line px-5 py-3 font-semibold text-purple"
            :disabled="busy"
            @click="close"
          >
            Cancelar
          </button>
          <button
            type="button"
            class="primary-button"
            :disabled="!selectedDrive || Boolean(directoryError) || busy"
            @click="send('ask')"
          >
            <LoadingSpinner v-if="busy" />
            <Send v-else :size="18" />
            {{ busy ? 'Enviando…' : 'Confirmar e enviar' }}
          </button>
        </footer>
      </template>
    </div>
  </div>
</template>
