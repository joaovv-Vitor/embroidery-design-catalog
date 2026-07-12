<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { AlertCircle, Clock3, RefreshCw, RotateCcw, Trash2 } from 'lucide-vue-next'

import RemovalConfirmModal from '@/components/catalog/RemovalConfirmModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import { apiErrorMessage } from '@/composables/useApiError'
import { catalogService } from '@/services/catalogService'
import type { DesenhoLixeira } from '@/types/api'

const items = ref<DesenhoLixeira[]>([])
const loading = ref(true)
const actionId = ref<number | null>(null)
const error = ref('')
const success = ref('')
const permanentTarget = ref<DesenhoLixeira | null>(null)
const permanentError = ref('')

const retentionNotice = computed(() => items.value[0]?.aviso)

async function loadTrash(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    items.value = await catalogService.trash()
  } catch (requestError) {
    error.value = apiErrorMessage(requestError, 'Não foi possível carregar a lixeira.')
  } finally {
    loading.value = false
  }
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function recoveryExpired(item: DesenhoLixeira): boolean {
  return new Date(item.recuperavel_ate).getTime() < Date.now()
}

async function restore(item: DesenhoLixeira): Promise<void> {
  actionId.value = item.id
  error.value = ''
  success.value = ''
  try {
    await catalogService.restoreDesign(item.id)
    items.value = items.value.filter((current) => current.id !== item.id)
    success.value = `${item.nome} foi restaurado para o catálogo.`
  } catch (requestError) {
    error.value = apiErrorMessage(requestError, 'Não foi possível restaurar o desenho.')
  } finally {
    actionId.value = null
  }
}

async function deletePermanently(): Promise<void> {
  if (!permanentTarget.value) return
  const target = permanentTarget.value
  actionId.value = target.id
  permanentError.value = ''

  try {
    await catalogService.deleteDesignPermanently(target.id)
    items.value = items.value.filter((item) => item.id !== target.id)
    permanentTarget.value = null
    success.value = `${target.nome} foi excluído permanentemente.`
  } catch (requestError) {
    permanentError.value = apiErrorMessage(requestError, 'Não foi possível excluir o desenho permanentemente.')
  } finally {
    actionId.value = null
  }
}

onMounted(loadTrash)
</script>

<template>
  <section class="mx-auto max-w-5xl">
    <header>
      <h1 class="font-serif text-4xl text-purple md:text-5xl">Lixeira</h1>
      <p class="mt-2 text-muted">Restaure desenhos removidos ou exclua seus arquivos permanentemente.</p>
    </header>

    <div
      v-if="retentionNotice"
      class="mt-7 flex items-start gap-3 rounded-2xl border border-line bg-amber-50 p-4 text-sm text-amber-800"
    >
      <AlertCircle :size="20" class="shrink-0" />
      {{ retentionNotice }}
    </div>

    <div v-if="error" class="mt-6 flex gap-2 rounded-xl bg-red-50 p-4 text-sm text-red-700" role="alert">
      <AlertCircle :size="19" class="shrink-0" />
      {{ error }}
    </div>
    <div v-if="success" class="mt-6 rounded-xl bg-green-50 p-4 text-sm text-green-700" role="status">
      {{ success }}
    </div>

    <div v-if="loading" class="mt-8 space-y-4">
      <div v-for="placeholder in 4" :key="placeholder" class="h-32 animate-pulse rounded-2xl bg-line/60"></div>
    </div>

    <div v-else-if="!items.length" class="mt-9 rounded-3xl border border-line bg-white p-12 text-center">
      <Trash2 class="mx-auto text-sage" :size="46" />
      <h2 class="mt-4 font-serif text-2xl text-purple">A lixeira está vazia</h2>
      <p class="mt-2 text-sm text-muted">Desenhos removidos do catálogo aparecerão aqui.</p>
    </div>

    <div v-else class="mt-8 space-y-4">
      <article
        v-for="item in items"
        :key="item.id"
        class="flex flex-col justify-between gap-5 rounded-2xl border border-line bg-white p-5 shadow-sm sm:flex-row sm:items-center"
      >
        <div class="min-w-0">
          <h2 class="truncate font-semibold text-purple">{{ item.nome }}</h2>
          <p class="mt-2 flex items-center gap-2 text-xs text-muted">
            <Clock3 :size="15" />
            Removido em {{ formatDate(item.excluido_em) }}
          </p>
          <p :class="['mt-1 text-xs', recoveryExpired(item) ? 'text-red-600' : 'text-sage']">
            {{ recoveryExpired(item)
              ? 'O prazo de recuperação expirou.'
              : `Pode ser recuperado até ${formatDate(item.recuperavel_ate)}.` }}
          </p>
        </div>

        <div class="flex flex-wrap gap-2">
          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-xl border border-line px-4 py-2 text-sm font-semibold text-purple disabled:opacity-50"
            :disabled="actionId !== null || recoveryExpired(item)"
            @click="restore(item)"
          >
            <LoadingSpinner v-if="actionId === item.id" />
            <RotateCcw v-else :size="17" />
            Restaurar
          </button>
          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-xl border border-red-200 px-4 py-2 text-sm font-semibold text-red-600 hover:bg-red-50"
            :disabled="actionId !== null"
            @click="permanentTarget = item"
          >
            <Trash2 :size="17" />
            Excluir definitivamente
          </button>
        </div>
      </article>
    </div>

    <button v-if="error && !loading" class="primary-button mt-5" @click="loadTrash">
      <RefreshCw :size="18" />
      Tentar novamente
    </button>
  </section>

  <RemovalConfirmModal
    v-if="permanentTarget"
    :design-name="permanentTarget.nome"
    permanent
    :loading="actionId === permanentTarget.id"
    :error="permanentError"
    @cancel="permanentTarget = null"
    @confirm="deletePermanently"
  />
</template>
