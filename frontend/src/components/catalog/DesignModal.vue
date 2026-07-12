<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { AlertCircle, CheckCircle2, Download, ImageOff, MapPin, Pencil, Star, X } from 'lucide-vue-next'

import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import { apiErrorMessage } from '@/composables/useApiError'
import { apiAssetUrl } from '@/services/api'
import { catalogService } from '@/services/catalogService'
import type { DesenhoDetalhe, MatrizVariacao } from '@/types/api'

const props = defineProps<{
  design: DesenhoDetalhe
  favoriteLoading?: boolean
}>()
const emit = defineEmits<{
  close: []
  edit: []
  favorite: [design: DesenhoDetalhe]
}>()

const numberFormatter = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 })
const pointsFormatter = new Intl.NumberFormat('pt-BR')
const titleId = `design-detail-title-${props.design.id}`
const downloadingId = ref<number | null>(null)
const downloadError = ref('')
const downloadSuccess = ref('')
let previousBodyOverflow = ''

function closeOnEscape(event: KeyboardEvent): void {
  if (event.key === 'Escape') emit('close')
}

async function downloadMatrix(matrix: MatrizVariacao): Promise<void> {
  downloadingId.value = matrix.id
  downloadError.value = ''
  downloadSuccess.value = ''

  try {
    const download = await catalogService.downloadMatrix(matrix.download_url)
    const objectUrl = URL.createObjectURL(download.blob)
    const anchor = document.createElement('a')
    anchor.href = objectUrl
    anchor.download = download.filename
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1000)
    downloadSuccess.value = `${download.filename} preparado para download.`
  } catch (error) {
    downloadError.value = apiErrorMessage(
      error,
      'O arquivo de backup desta matriz não está disponível para download.',
    )
  } finally {
    downloadingId.value = null
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
    class="fixed inset-0 z-[60] flex items-center justify-center bg-ink/60 p-3 backdrop-blur-sm sm:p-5"
    role="dialog"
    aria-modal="true"
    :aria-labelledby="titleId"
    @click.self="emit('close')"
  >
    <div
      class="grid max-h-[94vh] w-full max-w-[1000px] overflow-y-auto rounded-3xl bg-white shadow-2xl md:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]"
    >
      <div class="flex min-h-72 items-center justify-center bg-cream p-6 sm:min-h-96 sm:p-10">
        <img
          v-if="design.preview_url"
          :src="apiAssetUrl(design.preview_url)!"
          :alt="`Miniatura ampliada do bordado ${design.nome}`"
          class="max-h-[650px] w-full object-contain"
        />
        <div v-else class="flex flex-col items-center gap-3 text-muted">
          <ImageOff :size="48" />
          <span class="text-sm">Preview não disponível</span>
        </div>
      </div>

      <div class="relative p-6 sm:p-8">
        <button
          type="button"
          class="absolute right-5 top-5 rounded-full border border-line bg-white p-2 text-muted transition hover:text-purple"
          aria-label="Fechar detalhes"
          @click="emit('close')"
        >
          <X />
        </button>

        <div class="pr-14">
          <h2 :id="titleId" class="font-serif text-3xl text-purple sm:text-4xl">
            {{ design.nome }}
          </h2>
          <button
            type="button"
            class="mt-4 inline-flex items-center gap-2 rounded-full border border-line px-3 py-2 text-sm font-medium transition hover:bg-cream"
            :aria-label="design.favorito ? 'Remover desenho dos favoritos' : 'Adicionar desenho aos favoritos'"
            :aria-pressed="design.favorito"
            :disabled="favoriteLoading"
            @click="emit('favorite', design)"
          >
            <Star :size="19" :class="design.favorito ? 'fill-gold text-gold' : 'text-muted'" />
            {{ design.favorito ? 'Favorito' : 'Favoritar' }}
          </button>
          <button
            type="button"
            class="ml-2 mt-4 inline-flex items-center gap-2 rounded-full border border-line px-3 py-2 text-sm font-medium transition hover:bg-cream"
            @click="emit('edit')"
          >
            <Pencil :size="17" />
            Editar
          </button>
        </div>

        <span
          v-if="design.categoria"
          class="mt-5 inline-block rounded-full bg-[#EDF3ED] px-3 py-1 text-sm font-medium text-sage"
        >
          {{ design.categoria.nome }}
        </span>
        <span v-else class="mt-5 block text-sm text-muted">Sem categoria</span>

        <p v-if="design.descricao" class="mt-5 text-sm leading-6 text-muted">
          {{ design.descricao }}
        </p>

        <div class="mb-3 mt-8 flex items-center justify-between gap-3">
          <h3 class="font-semibold text-purple">Variações disponíveis</h3>
          <span class="text-xs text-muted">
            {{ design.matrizes.length }} {{ design.matrizes.length === 1 ? 'matriz' : 'matrizes' }}
          </span>
        </div>

        <div
          v-if="downloadError"
          class="mb-4 flex gap-2 rounded-xl bg-red-50 p-3 text-sm text-red-700"
          role="alert"
        >
          <AlertCircle :size="18" class="shrink-0" />
          {{ downloadError }}
        </div>
        <div
          v-if="downloadSuccess"
          class="mb-4 flex gap-2 rounded-xl bg-green-50 p-3 text-sm text-green-700"
          role="status"
        >
          <CheckCircle2 :size="18" class="shrink-0" />
          {{ downloadSuccess }}
        </div>

        <div class="space-y-4">
          <article
            v-for="item in design.matrizes"
            :key="item.id"
            class="rounded-2xl border border-line p-4"
          >
            <div class="flex flex-col items-start justify-between gap-4 sm:flex-row">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <h4 class="font-semibold text-ink">
                    {{ item.rotulo_tamanho || 'Variação sem rótulo' }}
                  </h4>
                  <span class="rounded-full bg-purple/10 px-2 py-1 text-xs font-semibold uppercase text-purple">
                    {{ item.formato }}
                  </span>
                </div>

                <dl class="mt-3 grid grid-cols-2 gap-x-5 gap-y-2 text-xs sm:grid-cols-3">
                  <div>
                    <dt class="text-muted">Dimensões</dt>
                    <dd class="mt-0.5 font-medium text-ink">
                      {{ numberFormatter.format(item.largura_mm) }} ×
                      {{ numberFormatter.format(item.altura_mm) }} mm
                    </dd>
                  </div>
                  <div>
                    <dt class="text-muted">Cores</dt>
                    <dd class="mt-0.5 font-medium text-ink">{{ item.quantidade_cores }}</dd>
                  </div>
                  <div>
                    <dt class="text-muted">Pontos</dt>
                    <dd class="mt-0.5 font-medium text-ink">
                      {{ pointsFormatter.format(item.quantidade_pontos) }}
                    </dd>
                  </div>
                </dl>
              </div>

              <button
                type="button"
                class="primary-button w-full shrink-0 !px-3 !py-2 text-sm sm:w-auto"
                :disabled="downloadingId !== null"
                @click="downloadMatrix(item)"
              >
                <LoadingSpinner v-if="downloadingId === item.id" />
                <Download v-else :size="17" />
                {{ downloadingId === item.id ? 'Baixando…' : 'Baixar .PES' }}
              </button>
            </div>

            <div
              v-if="item.origem_identificacao || item.caminho_relativo_origem"
              class="mt-4 flex gap-2 rounded-xl bg-cream p-3 text-xs text-muted"
            >
              <MapPin :size="16" class="mt-0.5 shrink-0" />
              <dl class="space-y-1">
                <div v-if="item.origem_identificacao">
                  <dt class="inline font-semibold text-ink">Origem:</dt>
                  <dd class="ml-1 inline">{{ item.origem_identificacao }}</dd>
                </div>
                <div v-if="item.caminho_relativo_origem">
                  <dt class="inline font-semibold text-ink">Pasta:</dt>
                  <dd class="ml-1 break-all font-mono">{{ item.caminho_relativo_origem }}</dd>
                </div>
              </dl>
            </div>
          </article>

          <p v-if="!design.matrizes.length" class="rounded-2xl bg-cream p-4 text-sm text-muted">
            Nenhuma variação disponível para este desenho.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
