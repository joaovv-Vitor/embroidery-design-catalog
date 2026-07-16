<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { FolderOpen, GalleryHorizontalEnd, RefreshCw, Search, Star, Upload, X } from 'lucide-vue-next'

import type { Categoria, DesenhoCard, DesenhoDetalhe, VitrineCriada } from '@catalogo-bordados/shared'
import { apiErrorMessage, createLatestRequestGuard } from '@catalogo-bordados/shared'
import { catalogService } from '@catalogo-runtime/services/catalogService'
import { catalogStore } from '@catalogo-runtime/services/catalogStore'
import { showcaseService } from '@catalogo-runtime/services/showcaseService'
import { copyText, shareOnWhatsApp } from '@catalogo-runtime/utils/share'

import DesignCard from '../components/catalog/DesignCard.vue'
import DesignEditModal from '../components/catalog/DesignEditModal.vue'
import DesignModal from '../components/catalog/DesignModal.vue'
import RemovalConfirmModal from '../components/catalog/RemovalConfirmModal.vue'
import ShowcaseCreateModal from '../components/showcase/ShowcaseCreateModal.vue'
import ShowcaseCreatedModal from '../components/showcase/ShowcaseCreatedModal.vue'
import LoadingSpinner from '../components/ui/LoadingSpinner.vue'

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
const selectionMode = ref(false)
const selected = ref<Map<number, DesenhoCard>>(new Map())
const creatingShowcase = ref(false)
const createModalOpen = ref(false)
const createError = ref('')
const createdShowcase = ref<VitrineCriada | null>(null)
const shareFeedback = ref('')

let searchTimer: number | undefined
let feedbackTimer: number | undefined
const catalogRequestGuard = createLatestRequestGuard()

const visibleItems = computed(() => items.value)
const visibleTotal = computed(() => total.value)

const selectedDesigns = computed(() => Array.from(selected.value.values()))

const hasActiveFilters = computed(() =>
  Boolean(query.value.trim() || favoritesOnly.value || selectedCategory.value !== null),
)

async function loadCatalog(): Promise<void> {
  const requestId = catalogRequestGuard.start()
  loading.value = true
  error.value = ''

  try {
    const result = await catalogStore.getCatalog({
      busca: query.value.trim() || undefined,
      categoria_id: selectedCategory.value ?? undefined,
      somente_favoritos: favoritesOnly.value || undefined,
      por_pagina: 24,
    })

    if (!catalogRequestGuard.isCurrent(requestId)) return
    items.value = result.itens
    total.value = result.total
  } catch (requestError) {
    if (!catalogRequestGuard.isCurrent(requestId)) return
    error.value = apiErrorMessage(requestError, 'Não foi possível carregar seu catálogo.')
  } finally {
    if (catalogRequestGuard.isCurrent(requestId)) loading.value = false
  }
}

async function loadCategories(): Promise<void> {
  try {
    categories.value = await catalogStore.getCategories()
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

function startSelection(): void {
  selectionMode.value = true
  closeDetail()
}

function cancelSelection(): void {
  selectionMode.value = false
  selected.value = new Map()
  createModalOpen.value = false
  createError.value = ''
}

function toggleSelection(design: DesenhoCard): void {
  const next = new Map(selected.value)
  if (next.has(design.id)) next.delete(design.id)
  else next.set(design.id, design)
  selected.value = next
}

function removeSelection(id: number): void {
  const next = new Map(selected.value)
  next.delete(id)
  selected.value = next
}

function openCreateShowcase(): void {
  if (!selectedDesigns.value.length) return
  createError.value = ''
  createModalOpen.value = true
}

async function createShowcase(data: { titulo?: string; nome_cliente?: string | null }): Promise<void> {
  if (!selectedDesigns.value.length) return
  creatingShowcase.value = true
  createError.value = ''
  try {
    createdShowcase.value = await showcaseService.create({
      desenho_ids: selectedDesigns.value.map((design) => design.id),
      ...data,
    })
    createModalOpen.value = false
    selectionMode.value = false
    selected.value = new Map()
  } catch (requestError) {
    createError.value = apiErrorMessage(requestError, 'Não foi possível criar a vitrine.')
  } finally {
    creatingShowcase.value = false
  }
}

async function copyCreatedLink(): Promise<void> {
  if (!createdShowcase.value) return
  try {
    await copyText(createdShowcase.value.link_publico)
    shareFeedback.value = 'Link copiado.'
  } catch (copyError) {
    shareFeedback.value = apiErrorMessage(copyError, 'Não foi possível copiar o link.')
  }
}

function shareCreatedOnWhatsApp(): void {
  if (!createdShowcase.value) return
  shareOnWhatsApp(createdShowcase.value.titulo, createdShowcase.value.link_publico)
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
    catalogStore.invalidateCatalog()
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
    catalogStore.invalidateCatalog()
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
  catalogStore.invalidateCatalog()
  await Promise.all([openDetail(designId), loadCatalog()])
}

watch(query, scheduleSearch)
watch([favoritesOnly, selectedCategory], loadCatalog)

onMounted(() => {
  loadCatalog()
  loadCategories()
})

onBeforeUnmount(() => {
  catalogRequestGuard.cancel()
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
      <div class="flex flex-wrap gap-3 self-start">
        <button
          v-if="!selectionMode"
          class="inline-flex items-center justify-center gap-2 rounded-xl border border-line bg-white px-5 py-3 font-semibold text-purple shadow-sm transition hover:bg-cream"
          @click="startSelection"
        >
          <GalleryHorizontalEnd :size="19" />
          Criar vitrine
        </button>
        <button v-else class="rounded-xl border border-line bg-white px-5 py-3 font-semibold text-purple" @click="cancelSelection">
          Cancelar seleção
        </button>
        <button class="primary-button" @click="router.push('/importar')">
          <Upload :size="19" />
          Importar matrizes
        </button>
      </div>
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
        :selection-mode="selectionMode"
        :selected="selected.has(design.id)"
        @open="openDetail"
        @favorite="toggleFavorite"
        @select="toggleSelection"
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

  <div
    v-if="selectionMode"
    class="fixed bottom-4 left-4 right-4 z-50 flex flex-col items-center justify-between gap-3 rounded-2xl border border-line bg-white p-4 shadow-2xl sm:flex-row md:left-[16rem] md:right-6 lg:px-6"
    role="status"
    aria-live="polite"
  >
    <div>
      <strong class="text-purple">{{ selectedDesigns.length }}</strong>
      <span class="ml-1 text-sm text-muted">{{ selectedDesigns.length === 1 ? 'desenho selecionado' : 'desenhos selecionados' }}</span>
    </div>
    <button class="primary-button w-full sm:w-auto" :disabled="!selectedDesigns.length" @click="openCreateShowcase">
      <GalleryHorizontalEnd :size="18" />
      Criar vitrine com {{ selectedDesigns.length }} {{ selectedDesigns.length === 1 ? 'desenho' : 'desenhos' }}
    </button>
  </div>

  <ShowcaseCreateModal
    v-if="createModalOpen"
    :designs="selectedDesigns"
    :loading="creatingShowcase"
    :error="createError"
    @close="createModalOpen = false"
    @remove="removeSelection"
    @create="createShowcase"
  />
  <ShowcaseCreatedModal
    v-if="createdShowcase"
    :showcase="createdShowcase"
    :feedback="shareFeedback"
    @close="createdShowcase = null; shareFeedback = ''"
    @copy="copyCreatedLink"
    @whatsapp="shareCreatedOnWhatsApp"
  />
</template>
