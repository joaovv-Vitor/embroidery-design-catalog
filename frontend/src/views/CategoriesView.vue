<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { AlertCircle, Edit3, Plus, Save, Tag, Trash2, X } from 'lucide-vue-next'

import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import { apiErrorMessage } from '@/composables/useApiError'
import { catalogService } from '@/services/catalogService'
import type { Categoria } from '@/types/api'

const DEFAULT_COLOR = '#7c6a8d'

const categories = ref<Categoria[]>([])
const loading = ref(true)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const error = ref('')
const success = ref('')
const formOpen = ref(false)
const editingId = ref<number | null>(null)
const name = ref('')
const color = ref(DEFAULT_COLOR)
const icon = ref('')

async function loadCategories(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    categories.value = await catalogService.categories()
  } catch (requestError) {
    error.value = apiErrorMessage(requestError, 'Não foi possível carregar as categorias.')
  } finally {
    loading.value = false
  }
}

function openCreateForm(): void {
  editingId.value = null
  name.value = ''
  color.value = DEFAULT_COLOR
  icon.value = ''
  error.value = ''
  success.value = ''
  formOpen.value = true
}

function openEditForm(category: Categoria): void {
  editingId.value = category.id
  name.value = category.nome
  color.value = category.cor || DEFAULT_COLOR
  icon.value = category.icone || ''
  error.value = ''
  success.value = ''
  formOpen.value = true
}

function closeForm(): void {
  if (saving.value) return
  formOpen.value = false
  editingId.value = null
}

async function saveCategory(): Promise<void> {
  const normalizedName = name.value.trim()
  if (!normalizedName) {
    error.value = 'Informe o nome da categoria.'
    return
  }

  saving.value = true
  error.value = ''
  success.value = ''

  try {
    const data = {
      nome: normalizedName,
      cor: color.value || null,
      icone: icon.value.trim() || null,
    }

    if (editingId.value === null) {
      await catalogService.createCategory(data)
      success.value = 'Categoria criada com sucesso.'
    } else {
      await catalogService.updateCategory(editingId.value, data)
      success.value = 'Categoria atualizada com sucesso.'
    }

    formOpen.value = false
    editingId.value = null
    await loadCategories()
  } catch (requestError) {
    error.value = apiErrorMessage(requestError, 'Não foi possível salvar a categoria.')
  } finally {
    saving.value = false
  }
}

async function deleteCategory(category: Categoria): Promise<void> {
  const confirmed = window.confirm(
    `Excluir a categoria “${category.nome}”? Esta ação não poderá ser desfeita.`,
  )
  if (!confirmed) return

  deletingId.value = category.id
  error.value = ''
  success.value = ''

  try {
    await catalogService.deleteCategory(category.id)
    categories.value = categories.value.filter((item) => item.id !== category.id)
    success.value = 'Categoria excluída com sucesso.'
  } catch (requestError) {
    error.value = apiErrorMessage(
      requestError,
      'Não foi possível excluir a categoria. Reclassifique os desenhos vinculados e tente novamente.',
    )
  } finally {
    deletingId.value = null
  }
}

onMounted(loadCategories)
</script>

<template>
  <section class="mx-auto max-w-5xl">
    <header class="flex flex-col justify-between gap-5 sm:flex-row sm:items-center">
      <div>
        <h1 class="font-serif text-4xl text-purple md:text-5xl">Categorias</h1>
        <p class="mt-2 text-muted">Organize seus desenhos por temas e encontre cada matriz com facilidade.</p>
      </div>
      <button class="primary-button self-start" @click="openCreateForm">
        <Plus :size="19" />
        Nova categoria
      </button>
    </header>

    <div
      v-if="error"
      class="mt-6 flex items-start gap-2 rounded-xl bg-red-50 p-4 text-sm text-red-700"
      role="alert"
    >
      <AlertCircle :size="19" class="shrink-0" />
      <span>{{ error }}</span>
    </div>
    <div v-if="success" class="mt-6 rounded-xl bg-green-50 p-4 text-sm text-green-700" role="status">
      {{ success }}
    </div>

    <div v-if="loading" class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="item in 6" :key="item" class="h-36 animate-pulse rounded-2xl bg-line/60"></div>
    </div>

    <div v-else-if="!categories.length" class="mt-9 rounded-3xl border border-line bg-white p-12 text-center">
      <Tag class="mx-auto text-sage" :size="46" />
      <h2 class="mt-4 font-serif text-2xl text-purple">Nenhuma categoria cadastrada</h2>
      <p class="mt-2 text-sm text-muted">Crie a primeira categoria para começar a organizar o catálogo.</p>
      <button class="primary-button mt-6" @click="openCreateForm">
        <Plus :size="18" />
        Criar categoria
      </button>
    </div>

    <div v-else class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <article
        v-for="category in categories"
        :key="category.id"
        class="group rounded-2xl border border-line bg-white p-5 shadow-sm transition hover:shadow-soft"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex min-w-0 items-center gap-3">
            <span
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-white shadow-sm"
              :style="{ backgroundColor: category.cor || DEFAULT_COLOR }"
            >
              <Tag :size="21" />
            </span>
            <div class="min-w-0">
              <h2 class="truncate font-semibold text-purple">{{ category.nome }}</h2>
              <p class="mt-1 truncate text-xs text-muted">
                {{ category.icone ? `Ícone: ${category.icone}` : 'Sem ícone personalizado' }}
              </p>
            </div>
          </div>
        </div>

        <div class="mt-5 flex gap-2 border-t border-line pt-4">
          <button
            type="button"
            class="inline-flex flex-1 items-center justify-center gap-2 rounded-xl border border-line px-3 py-2 text-sm font-medium text-purple transition hover:bg-cream"
            @click="openEditForm(category)"
          >
            <Edit3 :size="16" />
            Editar
          </button>
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-xl border border-line px-3 py-2 text-muted transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
            :aria-label="`Excluir categoria ${category.nome}`"
            :disabled="deletingId === category.id"
            @click="deleteCategory(category)"
          >
            <LoadingSpinner v-if="deletingId === category.id" />
            <Trash2 v-else :size="17" />
          </button>
        </div>
      </article>
    </div>

    <div class="mt-8 flex items-start gap-3 rounded-2xl border border-line bg-cream p-4 text-sm text-muted">
      <AlertCircle :size="19" class="shrink-0 text-terracotta" />
      <p>
        Categorias com desenhos vinculados não podem ser excluídas. Antes da exclusão, edite os desenhos e
        escolha outra categoria ou “Sem categoria”.
      </p>
    </div>

    <div
      v-if="formOpen"
      class="fixed inset-0 z-[70] flex items-center justify-center bg-ink/60 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="category-form-title"
      @click.self="closeForm"
    >
      <form class="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl sm:p-8" @submit.prevent="saveCategory">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h2 id="category-form-title" class="font-serif text-3xl text-purple">
              {{ editingId === null ? 'Nova categoria' : 'Editar categoria' }}
            </h2>
            <p class="mt-1 text-sm text-muted">O nome é obrigatório; cor e ícone são opcionais.</p>
          </div>
          <button
            type="button"
            class="rounded-full border border-line p-2 text-muted"
            aria-label="Fechar formulário"
            :disabled="saving"
            @click="closeForm"
          >
            <X />
          </button>
        </div>

        <div class="mt-7 space-y-5">
          <label class="block text-sm font-medium text-purple">
            Nome
            <input
              v-model="name"
              class="field mt-2"
              maxlength="120"
              placeholder="Ex.: Flores, Animais ou Natal"
              required
              autofocus
              :disabled="saving"
            />
          </label>
          <label class="block text-sm font-medium text-purple">
            Cor
            <span class="mt-2 flex items-center gap-3">
              <input
                v-model="color"
                type="color"
                class="h-11 w-16 cursor-pointer rounded-lg border border-line bg-white p-1"
                :disabled="saving"
              />
              <input v-model="color" class="field font-mono" maxlength="32" :disabled="saving" />
            </span>
          </label>
          <label class="block text-sm font-medium text-purple">
            Nome do ícone <span class="font-normal text-muted">(opcional)</span>
            <input
              v-model="icon"
              class="field mt-2"
              maxlength="80"
              placeholder="Ex.: flower, paw-print ou tree-pine"
              :disabled="saving"
            />
          </label>
        </div>

        <div class="mt-7 flex justify-end gap-3">
          <button
            type="button"
            class="rounded-xl border border-line px-5 py-3 font-semibold text-purple"
            :disabled="saving"
            @click="closeForm"
          >
            Cancelar
          </button>
          <button class="primary-button" :disabled="saving">
            <LoadingSpinner v-if="saving" />
            <Save v-else :size="18" />
            {{ saving ? 'Salvando…' : 'Salvar categoria' }}
          </button>
        </div>
      </form>
    </div>
  </section>
</template>
