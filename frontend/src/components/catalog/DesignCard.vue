<script setup lang="ts">
import { Check, ImageOff, Star } from 'lucide-vue-next'

import { apiAssetUrl } from '@/services/api'
import type { DesenhoCard } from '@/types/api'

defineProps<{
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
</script>

<template>
  <article
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
        v-if="design.preview_url"
        :src="apiAssetUrl(design.preview_url)!"
        :alt="`Preview de ${design.nome}`"
        class="h-full w-full object-contain"
      />
      <div v-else class="flex h-full items-center justify-center text-muted">
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
