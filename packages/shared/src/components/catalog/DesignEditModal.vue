<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { AlertCircle, Save, X } from 'lucide-vue-next'

import type { Categoria, DesenhoDetalhe } from '@catalogo-bordados/shared'
import { apiErrorMessage } from '@catalogo-bordados/shared'
import { catalogService } from '@catalogo-runtime/services/catalogService'

import LoadingSpinner from '../ui/LoadingSpinner.vue'

const props = defineProps<{
  design: DesenhoDetalhe
  categories: Categoria[]
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const name = ref(props.design.nome)
const categoryId = ref(props.design.categoria_id === null ? '' : String(props.design.categoria_id))
const matrices = ref(
  props.design.matrizes.map((matrix) => ({
    id: matrix.id,
    label: matrix.rotulo_tamanho || matrix.formato,
    origin: matrix.origem_identificacao || '',
    relativePath: matrix.caminho_relativo_origem || '',
  })),
)
const saving = ref(false)
const error = ref('')
let previousBodyOverflow = ''

function closeOnEscape(event: KeyboardEvent): void {
  if (event.key === 'Escape' && !saving.value) emit('close')
}

async function save(): Promise<void> {
  const normalizedName = name.value.trim()
  if (!normalizedName) {
    error.value = 'Informe o nome do desenho.'
    return
  }

  saving.value = true
  error.value = ''

  try {
    await catalogService.updateDesign(props.design.id, {
      nome: normalizedName,
      categoria_id: categoryId.value ? Number(categoryId.value) : null,
    })

    for (const matrix of matrices.value) {
      await catalogService.updateMatrix(matrix.id, {
        identificacao_origem: matrix.origin.trim() || null,
        caminho_relativo_origem: matrix.relativePath.trim() || null,
      })
    }

    emit('saved')
  } catch (requestError) {
    error.value = apiErrorMessage(requestError, 'Não foi possível salvar as alterações.')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  previousBodyOverflow = document.body.style.overflow
  document.body.style.overflow = 'hidden'
  window.addEventListener('keydown', closeOnEscape)
})

onBeforeUnmount(() => {
  document.body.style.overflow = previousBodyOverflow
  window.removeEventListener('keydown', closeOnEscape)
})
</script>

<template>
  <div
    class="fixed inset-0 z-[70] flex items-center justify-center bg-ink/60 p-3 backdrop-blur-sm sm:p-5"
    role="dialog"
    aria-modal="true"
    aria-labelledby="edit-design-title"
    @click.self="!saving && emit('close')"
  >
    <form
      class="max-h-[94vh] w-full max-w-2xl overflow-y-auto rounded-3xl bg-white p-6 shadow-2xl sm:p-8"
      @submit.prevent="save"
    >
      <div class="flex items-start justify-between gap-4">
        <div>
          <h2 id="edit-design-title" class="font-serif text-3xl text-purple">Editar desenho</h2>
          <p class="mt-1 text-sm text-muted">As alterações afetam somente os dados do catálogo.</p>
        </div>
        <button
          type="button"
          class="rounded-full border border-line p-2 text-muted"
          aria-label="Cancelar edição"
          :disabled="saving"
          @click="emit('close')"
        >
          <X />
        </button>
      </div>

      <div class="mt-7 grid gap-5 sm:grid-cols-2">
        <label class="text-sm font-medium text-purple sm:col-span-2">
          Nome do desenho
          <input v-model="name" class="field mt-2" maxlength="255" required :disabled="saving" />
        </label>
        <label class="text-sm font-medium text-purple sm:col-span-2">
          Categoria principal
          <select v-model="categoryId" class="field mt-2" :disabled="saving">
            <option value="">Sem categoria</option>
            <option v-for="category in categories" :key="category.id" :value="String(category.id)">
              {{ category.nome }}
            </option>
          </select>
        </label>
      </div>

      <div class="mt-8">
        <h3 class="font-semibold text-purple">Origem das variações</h3>
        <p class="mt-1 text-xs text-muted">O arquivo .PES de backup não será modificado.</p>

        <div class="mt-4 space-y-4">
          <fieldset
            v-for="matrix in matrices"
            :key="matrix.id"
            class="rounded-2xl border border-line p-4"
          >
            <legend class="px-2 text-sm font-semibold text-ink">{{ matrix.label }}</legend>
            <div class="grid gap-4 sm:grid-cols-2">
              <label class="text-xs font-medium text-purple">
                Identificação da origem
                <input
                  v-model="matrix.origin"
                  class="field mt-2"
                  maxlength="255"
                  placeholder="Ex.: Pendrive Azul"
                  :disabled="saving"
                />
              </label>
              <label class="text-xs font-medium text-purple">
                Caminho relativo
                <input
                  v-model="matrix.relativePath"
                  class="field mt-2"
                  maxlength="1024"
                  placeholder="Ex.: flores/rosas/modelo.pes"
                  :disabled="saving"
                />
              </label>
            </div>
          </fieldset>

          <p v-if="!matrices.length" class="rounded-xl bg-cream p-4 text-sm text-muted">
            Este desenho não possui variações para editar.
          </p>
        </div>
      </div>

      <div v-if="error" class="mt-5 flex gap-2 rounded-xl bg-red-50 p-4 text-sm text-red-700" role="alert">
        <AlertCircle :size="19" class="shrink-0" />
        {{ error }}
      </div>

      <div class="mt-7 flex flex-wrap justify-end gap-3">
        <button
          type="button"
          class="rounded-xl border border-line px-5 py-3 font-semibold text-purple"
          :disabled="saving"
          @click="emit('close')"
        >
          Cancelar
        </button>
        <button class="primary-button" :disabled="saving">
          <LoadingSpinner v-if="saving" />
          <Save v-else :size="18" />
          {{ saving ? 'Salvando…' : 'Salvar alterações' }}
        </button>
      </div>
    </form>
  </div>
</template>
