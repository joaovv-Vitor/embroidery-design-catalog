<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { Check, ImageOff, Star } from 'lucide-vue-next'

import type { DesenhoCard } from '@catalogo-bordados/shared'
import { apiAssetUrl } from '@catalogo-runtime/services/api'

const props = defineProps<{
  design: DesenhoCard
  favoriteLoading?: boolean
  selectionMode?: boolean
  selected?: boolean
}>()

defineEmits<{
  open: [id: number]
  favorite: [design: DesenhoCard]
  select: [design: DesenhoCard]
}>()

const PREVIEW_ROOT_MARGIN = '300px 0px'

const card = ref<HTMLElement | null>(null)
const previewStatus = ref<'waiting' | 'loading' | 'loaded' | 'failed' | 'missing'>(
  props.design.preview_url ? 'waiting' : 'missing',
)
const previewUrl = computed(() => apiAssetUrl(props.design.preview_url))
let observer: IntersectionObserver | null = null

function loadPreview(): void {
  if (previewStatus.value !== 'waiting') return
  previewStatus.value = 'loading'
  observer?.disconnect()
}

function handlePreviewLoad(): void {
  previewStatus.value = 'loaded'
}

function handlePreviewError(): void {
  previewStatus.value = 'failed'
}

onMounted(() => {
  if (!previewUrl.value) return
  if (!('IntersectionObserver' in window)) {
    loadPreview()
    return
  }

  observer = new IntersectionObserver(
    (entries) => {
      if (entries.some((entry) => entry.isIntersecting)) loadPreview()
    },
    { rootMargin: PREVIEW_ROOT_MARGIN },
  )
  if (card.value) observer.observe(card.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
})
</script>

<template>
  <article
    ref="card"
    class="group cursor-pointer overflow-hidden rounded-[18px] border border-line bg-white shadow-sm transition duration-200 hover:-translate-y-1 hover:shadow-soft"
    tabindex="0"
    :class="selected ? 'ring-2 ring-terracotta ring-offset-2' : ''"
    :aria-pressed="selectionMode ? selected : undefined"
    @click="selectionMode ? $emit('select', design) : $emit('open', design.id)"
    @keydown.enter="selectionMode ? $emit('select', design) : $emit('open', design.id)"
    @keydown.space.prevent="selectionMode ? $emit('select', design) : $emit('open', design.id)"
  >
    <div class="relative aspect-square bg-cream p-5">
      <img
        v-if="previewUrl && (previewStatus === 'loading' || previewStatus === 'loaded')"
        :src="previewUrl!"
        :alt="`Preview de ${design.nome}`"
        class="h-full w-full object-contain transition-opacity duration-200"
        :class="previewStatus === 'loaded' ? 'opacity-100' : 'opacity-0'"
        loading="lazy"
        decoding="async"
        @load="handlePreviewLoad"
        @error="handlePreviewError"
      />
      <div
        v-if="previewStatus === 'waiting' || previewStatus === 'loading'"
        class="absolute inset-5 animate-pulse rounded-2xl bg-line/70"
        aria-label="Carregando preview"
      ></div>
      <div v-else-if="previewStatus === 'failed' || previewStatus === 'missing'" class="flex h-full items-center justify-center text-muted">
        <ImageOff :size="32" />
      </div>

      <span
        v-if="selectionMode"
        :class="[
          'absolute right-3 top-3 flex h-9 w-9 items-center justify-center rounded-full border-2 shadow-sm transition',
          selected ? 'border-terracotta bg-terracotta text-white' : 'border-white bg-white/95 text-muted',
        ]"
        aria-hidden="true"
      >
        <Check v-if="selected" :size="20" />
      </span>
      <button
        v-else
        type="button"
        :aria-label="design.favorito ? 'Remover favorito' : 'Adicionar favorito'"
        :aria-pressed="design.favorito"
        :disabled="favoriteLoading"
        class="absolute right-3 top-3 rounded-full bg-white/95 p-2 shadow-sm transition hover:scale-105 disabled:cursor-wait disabled:opacity-60"
        @click.stop="$emit('favorite', design)"
        @keydown.stop
      >
        <Star :size="20" :class="design.favorito ? 'fill-gold text-gold' : 'text-muted'" />
      </button>
    </div>

    <div class="p-4">
      <h2 class="truncate font-semibold text-purple">{{ design.nome }}</h2>
      <span
        v-if="design.categoria"
        class="mt-3 inline-block rounded-full bg-[#EDF3ED] px-3 py-1 text-xs font-medium text-sage"
      >
        {{ design.categoria.nome }}
      </span>
      <span v-else class="mt-3 block text-xs text-muted">Sem categoria</span>
    </div>
  </article>
</template>
