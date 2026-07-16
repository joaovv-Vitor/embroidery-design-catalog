<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { AlertCircle, CalendarDays, ImageOff, Scissors, X } from 'lucide-vue-next'
import { useRoute } from 'vue-router'

import {
  apiErrorMessage,
  type ItemVitrinePublica,
  type VitrinePublica,
} from '@catalogo-bordados/shared'
import LoadingSpinner from '@catalogo-bordados/shared/components/ui/LoadingSpinner.vue'

import { apiAssetUrl } from '@/services/api'
import { showcaseService } from '@/services/showcaseService'

const route = useRoute()
const showcase = ref<VitrinePublica | null>(null)
const loading = ref(true)
const error = ref('')
const enlargedItem = ref<ItemVitrinePublica | null>(null)

const token = computed(() => String(route.params.token || ''))

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'long' }).format(new Date(value))
}

async function loadShowcase(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    showcase.value = await showcaseService.publicDetail(token.value)
  } catch (requestError) {
    error.value = apiErrorMessage(requestError, 'Esta vitrine não está disponível ou o link é inválido.')
  } finally {
    loading.value = false
  }
}

onMounted(loadShowcase)
</script>

<template>
  <div class="min-h-screen bg-[#fffaf6] text-ink">
    <header class="border-b border-line bg-white/90 px-5 py-4 backdrop-blur sm:px-8">
      <div class="mx-auto flex max-w-6xl items-center gap-3 text-purple">
        <span class="rounded-xl bg-cream p-2"><Scissors :size="23" /></span>
        <span class="font-serif text-xl">Catálogo de Bordados</span>
      </div>
    </header>

    <main class="mx-auto max-w-6xl px-4 py-8 sm:px-8 sm:py-12">
      <div v-if="loading" class="flex min-h-[55vh] items-center justify-center text-purple">
        <LoadingSpinner />
        <span class="ml-3 text-sm text-muted">Carregando opções de bordado…</span>
      </div>

      <section v-else-if="error" class="mx-auto mt-16 max-w-xl rounded-3xl border border-line bg-white p-8 text-center shadow-soft sm:p-12">
        <AlertCircle class="mx-auto text-terracotta" :size="45" />
        <h1 class="mt-5 font-serif text-3xl text-purple">Vitrine indisponível</h1>
        <p class="mt-3 leading-7 text-muted">{{ error }}</p>
      </section>

      <template v-else-if="showcase">
        <section class="text-center">
          <p v-if="showcase.nome_cliente" class="text-sm font-semibold uppercase tracking-[0.2em] text-terracotta">Especialmente para {{ showcase.nome_cliente }}</p>
          <h1 class="mt-3 font-serif text-4xl text-purple sm:text-5xl lg:text-6xl">{{ showcase.titulo }}</h1>
          <p class="mx-auto mt-4 max-w-2xl text-muted">Selecione uma opção para visualizar o bordado em tamanho ampliado.</p>
          <p class="mt-4 inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-xs text-muted shadow-sm">
            <CalendarDays :size="15" /> Disponível até {{ formatDate(showcase.expira_em) }}
          </p>
        </section>

        <section class="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3" aria-label="Opções de bordado">
          <button
            v-for="item in showcase.itens"
            :key="item.numero"
            type="button"
            class="group overflow-hidden rounded-3xl border border-line bg-white text-left shadow-sm transition hover:-translate-y-1 hover:shadow-soft"
            @click="enlargedItem = item"
          >
            <div class="relative aspect-square bg-cream p-5 sm:p-7">
              <span class="absolute left-4 top-4 z-10 flex h-9 min-w-9 items-center justify-center rounded-full bg-purple px-2 text-sm font-bold text-white shadow">{{ item.numero }}</span>
              <img v-if="item.preview_url" :src="apiAssetUrl(item.preview_url)!" :alt="`Preview de ${item.nome}`" class="h-full w-full object-contain transition duration-300 group-hover:scale-[1.03]" />
              <div v-else class="flex h-full flex-col items-center justify-center gap-3 text-muted"><ImageOff :size="36" /><span class="text-sm">Preview indisponível</span></div>
            </div>
            <div class="p-5"><h2 class="text-lg font-semibold text-purple">{{ item.nome }}</h2><p class="mt-1 text-sm text-muted">Opção {{ item.numero }}</p></div>
          </button>
        </section>
      </template>
    </main>

    <div v-if="enlargedItem" class="fixed inset-0 z-50 flex items-center justify-center bg-ink/85 p-4 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="public-preview-title" @click.self="enlargedItem = null">
      <div class="relative w-full max-w-4xl rounded-3xl bg-white p-4 shadow-2xl sm:p-7">
        <button class="absolute right-4 top-4 z-10 rounded-full bg-white p-2 text-muted shadow" aria-label="Fechar preview" @click="enlargedItem = null"><X /></button>
        <div class="flex max-h-[72vh] min-h-72 items-center justify-center rounded-2xl bg-cream p-5">
          <img v-if="enlargedItem.preview_url" :src="apiAssetUrl(enlargedItem.preview_url)!" :alt="`Preview ampliada de ${enlargedItem.nome}`" class="max-h-[68vh] max-w-full object-contain" />
          <ImageOff v-else :size="48" class="text-muted" />
        </div>
        <div class="flex items-center gap-3 px-2 pb-1 pt-5"><span class="flex h-9 min-w-9 items-center justify-center rounded-full bg-purple px-2 text-sm font-bold text-white">{{ enlargedItem.numero }}</span><h2 id="public-preview-title" class="font-serif text-2xl text-purple">{{ enlargedItem.nome }}</h2></div>
      </div>
    </div>
  </div>
</template>
