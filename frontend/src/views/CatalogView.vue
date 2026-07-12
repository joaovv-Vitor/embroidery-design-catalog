<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { FolderOpen, RefreshCw, Search, Star, Upload, X } from 'lucide-vue-next'

import DesignCard from '@/components/catalog/DesignCard.vue'
import DesignEditModal from '@/components/catalog/DesignEditModal.vue'
import DesignModal from '@/components/catalog/DesignModal.vue'
import RemovalConfirmModal from '@/components/catalog/RemovalConfirmModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import { apiErrorMessage } from '@/composables/useApiError'
import { catalogService } from '@/services/catalogService'
import type { Categoria, DesenhoCard, DesenhoDetalhe } from '@/types/api'

const SEARCH_DEBOUNCE_MS = 300

const router = useRouter()
const items = ref<DesenhoCard[]>([])
const categories = ref<Categoria[]>([])
const total = ref(0)
const loading = ref(true)
const error = ref('')
const query = ref('')
const selectedCategory = ref<number | null>(null)
const favoritesOnly = ref(false)
const detail = ref<DesenhoDetalhe | null>(null)
const detailLoading = ref(false)
const editingDetail = ref(false)
const confirmingRemoval = ref(false)
const removalLoading = ref(false)
const removalError = ref('')
const favoritePendingIds = ref<Set<number>>(new Set())
const favoriteFeedback = ref('')

let searchTimer: number | undefined
let feedbackTimer: number | undefined
let latestRequest = 0

const visibleItems = computed(() => {
  if (selectedCategory.value === null) return items.value
  return items.value.filter((design) => design.categoria?.id === selectedCategory.value)
})

const visibleTotal = computed(() =>
  selectedCategory.value === null ? total.value : visibleItems.value.length,
)

const hasActiveFilters = computed(() =>
  Boolean(query.value.trim() || favoritesOnly.value || selectedCategory.value !== null),
)

async function loadCatalog(): Promise<void> {
  const requestId = ++latestRequest
  loading.value = true
  error.value = ''

  try {
    const result = await catalogService.list({
      busca: query.value.trim() || undefined,
      favorito: favoritesOnly.value || undefined,
      por_pagina: 100,
    })

    if (requestId !== latestRequest) return
    items.value = result.itens
    total.value = result.total
  } catch (requestError) {
    if (requestId !== latestRequest) return
    error.value = apiErrorMessage(requestError, 'Não foi possível carregar seu catálogo.')
  } finally {
    if (requestId === latestRequest) loading.value = false
  }
}

async function loadCategories(): Promise<void> {
  try {
    categories.value = await catalogService.categories()
  } catch {
    // A pesquisa continua disponível mesmo quando as categorias não carregam.
  }
}

function scheduleSearch(): void {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(loadCatalog, SEARCH_DEBOUNCE_MS)
}

function clearSearch(): void {
  query.value = ''
}

function selectAll(): void {
  selectedCategory.value = null
  favoritesOnly.value = false
}

function selectCategory(categoryId: number): void {
  selectedCategory.value = categoryId
  favoritesOnly.value = false
}

function toggleFavoritesFilter(): void {
  favoritesOnly.value = !favoritesOnly.value
  selectedCategory.value = null
}

async function toggleFavorite(design: DesenhoCard | DesenhoDetalhe): Promise<void> {
  if (favoritePendingIds.value.has(design.id)) return

  const previousValue = design.favorito
  const newValue = !previousValue
  const catalogCard = items.value.find((item) => item.id === design.id)
  const openDetail = detail.value?.id === design.id ? detail.value : null

  favoritePendingIds.value = new Set(favoritePendingIds.value).add(design.id)
  favoriteFeedback.value = ''

  design.favorito = newValue
  if (catalogCard) catalogCard.favorito = newValue
  if (openDetail) openDetail.favorito = newValue

  try {
    await catalogService.favorite(design.id, newValue)
    if (favoritesOnly.value && previousValue) {
      items.value = items.value.filter((item) => item.id !== design.id)
      total.value = Math.max(0, total.value - 1)
    }
    showFavoriteFeedback(newValue ? 'Desenho adicionado aos favoritos.' : 'Desenho removido dos favoritos.')
  } catch (requestError) {
    design.favorito = previousValue
    if (catalogCard) catalogCard.favorito = previousValue
    if (openDetail) openDetail.favorito = previousValue
    showFavoriteFeedback(apiErrorMessage(requestError, 'Não foi possível atualizar o favorito.'))
  } finally {
    const pendingIds = new Set(favoritePendingIds.value)
    pendingIds.delete(design.id)
    favoritePendingIds.value = pendingIds
  }
}

function showFavoriteFeedback(message: string): void {
  window.clearTimeout(feedbackTimer)
  favoriteFeedback.value = message
  feedbackTimer = window.setTimeout(() => {
    favoriteFeedback.value = ''
  }, 3000)
}

async function openDetail(id: number): Promise<void> {
  detailLoading.value = true
  editingDetail.value = false
  try {
    detail.value = await catalogService.detail(id)
  } catch (detailError) {
    error.value = apiErrorMessage(detailError, 'Não foi possível abrir os detalhes.')
  } finally {
    detailLoading.value = false
  }
}

function closeDetail(): void {
  editingDetail.value = false
  confirmingRemoval.value = false
  detail.value = null
}

async function moveDetailToTrash(): Promise<void> {
  if (!detail.value) return
  removalLoading.value = true
  removalError.value = ''

  try {
    const designId = detail.value.id
    await catalogService.moveToTrash(designId)
    items.value = items.value.filter((item) => item.id !== designId)
    total.value = Math.max(0, total.value - 1)
    closeDetail()
    showFavoriteFeedback('Desenho movido para a lixeira.')
  } catch (requestError) {
    removalError.value = apiErrorMessage(requestError, 'Não foi possível mover o desenho para a lixeira.')
  } finally {
    removalLoading.value = false
  }
}

async function handleEditSaved(): Promise<void> {
  if (!detail.value) return
  const designId = detail.value.id
  editingDetail.value = false
  await Promise.all([openDetail(designId), loadCatalog()])
}

watch(query, scheduleSearch)
watch(favoritesOnly, loadCatalog)

onMounted(() => {
  loadCatalog()
  loadCategories()
})

onBeforeUnmount(() => {
  window.clearTimeout(searchTimer)
  window.clearTimeout(feedbackTimer)
})
</script>

<template>
  <section class="mx-auto max-w-[1500px]" :aria-busy="loading">
    <header class="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">
      <div>
        <h1 class="font-serif text-4xl text-purple md:text-5xl">Seu catálogo de bordados</h1>
        <p class="mt-2 text-muted">Encontre rapidamente a matriz que você precisa.</p>
      </div>
      <button class="primary-button self-start" @click="router.push('/importar')">
        <Upload :size="19" />
        Importar matrizes
      </button>
    </header>

    <div class="mt-9 flex flex-col items-stretch gap-3 lg:flex-row lg:items-center">
      <label class="relative flex-1">
        <span class="sr-only">Pesquisar desenhos por nome ou categoria</span>
        <Search class="absolute left-4 top-1/2 -translate-y-1/2 text-muted" :size="21" />
        <input
          v-model="query"
          type="search"
          class="field py-4 pl-12 pr-12 text-base"
          placeholder="Busque por nome ou categoria"
          autocomplete="off"
        />
        <button
          v-if="query"
          type="button"
          class="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-2 text-muted hover:bg-cream hover:text-purple"
          aria-label="Limpar pesquisa"
          @click="clearSearch"
        >
          <X :size="18" />
        </button>
      </label>

      <p class="whitespace-nowrap text-sm text-muted" aria-live="polite">
        <strong class="text-purple">{{ visibleTotal }}</strong>
        {{ visibleTotal === 1 ? 'desenho encontrado' : 'desenhos encontrados' }}
      </p>
    </div>

    <div class="mt-5 flex flex-wrap gap-2" aria-label="Filtros do catálogo">
      <button
        :class="[
          'rounded-full px-4 py-2 text-sm font-medium transition',
          selectedCategory === null && !favoritesOnly
            ? 'bg-terracotta text-white'
            : 'border border-line bg-white text-muted',
        ]"
        @click="selectAll"
      >
        Todos
      </button>
      <button
        v-for="category in categories"
        :key="category.id"
        :class="[
          'rounded-full px-4 py-2 text-sm font-medium transition',
          selectedCategory === category.id
            ? 'bg-terracotta text-white'
            : 'border border-line bg-white text-muted',
        ]"
        @click="selectCategory(category.id)"
      >
        {{ category.nome }}
      </button>
      <button
        :class="[
          'flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition',
          favoritesOnly ? 'bg-gold text-white' : 'border border-line bg-white text-muted',
        ]"
        :aria-pressed="favoritesOnly"
        @click="toggleFavoritesFilter"
      >
        <Star :size="16" :class="favoritesOnly ? 'fill-white' : ''" />
        Favoritos
      </button>
    </div>

    <div v-if="loading" class="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <div
        v-for="placeholder in 8"
        :key="placeholder"
        class="overflow-hidden rounded-[18px] border border-line bg-white"
      >
        <div class="aspect-square animate-pulse bg-line/60"></div>
        <div class="space-y-3 p-4">
          <div class="h-4 w-2/3 animate-pulse rounded bg-line"></div>
          <div class="h-6 w-1/3 animate-pulse rounded-full bg-line"></div>
        </div>
      </div>
    </div>

    <div v-else-if="error" class="mt-12 rounded-2xl border border-line bg-white p-10 text-center">
      <p class="text-muted">{{ error }}</p>
      <button class="primary-button mt-5" @click="loadCatalog">
        <RefreshCw :size="18" />
        Tentar novamente
      </button>
    </div>

    <div
      v-else-if="!visibleItems.length"
      class="mt-12 rounded-2xl border border-line bg-white p-12 text-center"
    >
      <FolderOpen class="mx-auto text-sage" :size="42" />
      <h2 class="mt-4 font-serif text-2xl text-purple">
        {{ hasActiveFilters ? 'Nenhum desenho encontrado' : 'Seu catálogo está esperando o primeiro bordado' }}
      </h2>
      <p class="mt-2 text-sm text-muted">
        {{ hasActiveFilters ? 'Tente ajustar sua busca ou os filtros.' : 'Importe uma matriz .PES para começar.' }}
      </p>
    </div>

    <div v-else class="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <DesignCard
        v-for="design in visibleItems"
        :key="design.id"
        :design="design"
        :favorite-loading="favoritePendingIds.has(design.id)"
        @open="openDetail"
        @favorite="toggleFavorite"
      />
    </div>
  </section>

  <div
    v-if="detailLoading"
    class="fixed inset-0 z-[60] flex items-center justify-center bg-ink/60 text-white"
  >
    <LoadingSpinner />
  </div>
  <DesignModal
    v-if="detail && !editingDetail && !confirmingRemoval"
    :design="detail"
    :favorite-loading="favoritePendingIds.has(detail.id)"
    @close="closeDetail"
    @edit="editingDetail = true"
    @favorite="toggleFavorite"
    @remove="confirmingRemoval = true"
  />
  <DesignEditModal
    v-if="detail && editingDetail"
    :design="detail"
    :categories="categories"
    @close="editingDetail = false"
    @saved="handleEditSaved"
  />
  <RemovalConfirmModal
    v-if="detail && confirmingRemoval"
    :design-name="detail.nome"
    :loading="removalLoading"
    :error="removalError"
    @cancel="confirmingRemoval = false"
    @confirm="moveDetailToTrash"
  />

  <div
    v-if="favoriteFeedback"
    class="fixed bottom-5 right-5 z-[80] max-w-sm rounded-xl bg-purple px-4 py-3 text-sm font-medium text-white shadow-soft"
    role="status"
    aria-live="polite"
  >
    {{ favoriteFeedback }}
  </div>
</template>
