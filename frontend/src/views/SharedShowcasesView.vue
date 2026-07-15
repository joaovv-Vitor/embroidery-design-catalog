<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { AlertCircle, CalendarDays, Copy, GalleryHorizontalEnd, MessageCircle, Power, RefreshCw, Trash2 } from 'lucide-vue-next'

import ShowcaseActionModal from '@/components/showcase/ShowcaseActionModal.vue'
import { apiErrorMessage } from '@/composables/useApiError'
import { showcaseService } from '@/services/showcaseService'
import type { VitrineGerencial } from '@/types/api'
import { copyText, shareOnWhatsApp } from '@/utils/share'

const items = ref<VitrineGerencial[]>([])
const loading = ref(true)
const error = ref('')
const success = ref('')
const target = ref<VitrineGerencial | null>(null)
const action = ref<'deactivate' | 'delete' | null>(null)
const actionLoading = ref(false)
const actionError = ref('')

const modalTitle = computed(() => action.value === 'delete' ? 'Excluir vitrine permanentemente?' : 'Desativar esta vitrine?')
const modalDescription = computed(() => action.value === 'delete'
  ? `A seleção “${target.value?.titulo ?? ''}” e suas previews serão removidas. Os desenhos continuarão no catálogo.`
  : `O link de “${target.value?.titulo ?? ''}” deixará de funcionar imediatamente para o cliente.`)

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium' }).format(new Date(value))
}

function statusLabel(status: VitrineGerencial['status']): string {
  return { ativa: 'Ativa', expirada: 'Expirada', desativada: 'Desativada' }[status]
}

function statusClass(status: VitrineGerencial['status']): string {
  return {
    ativa: 'bg-green-50 text-green-700',
    expirada: 'bg-amber-50 text-amber-800',
    desativada: 'bg-gray-100 text-gray-600',
  }[status]
}

async function loadShowcases(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    items.value = await showcaseService.list()
  } catch (requestError) {
    error.value = apiErrorMessage(requestError, 'Não foi possível carregar as vitrines compartilhadas.')
  } finally {
    loading.value = false
  }
}

async function copyLink(showcase: VitrineGerencial): Promise<void> {
  if (!showcase.link_publico) return
  try {
    await copyText(showcase.link_publico)
    success.value = `Link de “${showcase.titulo}” copiado.`
  } catch (copyError) {
    error.value = apiErrorMessage(copyError, 'Não foi possível copiar o link.')
  }
}

function share(showcase: VitrineGerencial): void {
  if (showcase.link_publico) shareOnWhatsApp(showcase.titulo, showcase.link_publico)
}

function requestAction(showcase: VitrineGerencial, requestedAction: 'deactivate' | 'delete'): void {
  target.value = showcase
  action.value = requestedAction
  actionError.value = ''
}

function closeAction(): void {
  if (actionLoading.value) return
  target.value = null
  action.value = null
  actionError.value = ''
}

async function confirmAction(): Promise<void> {
  if (!target.value || !action.value) return
  actionLoading.value = true
  actionError.value = ''
  const current = target.value
  try {
    if (action.value === 'deactivate') {
      await showcaseService.updateStatus(current.id, false)
      success.value = `A vitrine “${current.titulo}” foi desativada.`
    } else {
      await showcaseService.deletePermanently(current.id)
      success.value = `A vitrine “${current.titulo}” foi excluída permanentemente.`
    }
    closeActionAfterSuccess()
    await loadShowcases()
  } catch (requestError) {
    actionError.value = apiErrorMessage(requestError, 'Não foi possível concluir a ação.')
  } finally {
    actionLoading.value = false
  }
}

function closeActionAfterSuccess(): void {
  target.value = null
  action.value = null
  actionError.value = ''
}

onMounted(loadShowcases)
</script>

<template>
  <section class="mx-auto max-w-6xl">
    <header>
      <h1 class="font-serif text-4xl text-purple md:text-5xl">Vitrines compartilhadas</h1>
      <p class="mt-2 text-muted">Acompanhe os links enviados e controle quais opções continuam disponíveis.</p>
    </header>

    <div v-if="error" class="mt-6 flex items-start gap-2 rounded-xl bg-red-50 p-4 text-sm text-red-700" role="alert"><AlertCircle :size="19" class="shrink-0" />{{ error }}</div>
    <div v-if="success" class="mt-6 rounded-xl bg-green-50 p-4 text-sm text-green-700" role="status">{{ success }}</div>

    <div v-if="loading" class="mt-8 space-y-4"><div v-for="item in 4" :key="item" class="h-44 animate-pulse rounded-2xl bg-line/60"></div></div>
    <div v-else-if="!items.length" class="mt-9 rounded-3xl border border-line bg-white p-12 text-center">
      <GalleryHorizontalEnd class="mx-auto text-sage" :size="48" />
      <h2 class="mt-4 font-serif text-2xl text-purple">Nenhuma vitrine compartilhada</h2>
      <p class="mt-2 text-sm text-muted">Selecione desenhos no catálogo para criar sua primeira vitrine.</p>
      <router-link to="/" class="primary-button mt-6">Abrir catálogo</router-link>
    </div>

    <div v-else class="mt-8 space-y-4">
      <article v-for="showcase in items" :key="showcase.id" class="rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-6">
        <div class="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-3"><h2 class="truncate text-lg font-semibold text-purple">{{ showcase.titulo }}</h2><span :class="['rounded-full px-3 py-1 text-xs font-semibold', statusClass(showcase.status)]">{{ statusLabel(showcase.status) }}</span></div>
            <div class="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted">
              <span>{{ showcase.quantidade_desenhos }} {{ showcase.quantidade_desenhos === 1 ? 'desenho' : 'desenhos' }}</span>
              <span class="inline-flex items-center gap-2"><CalendarDays :size="16" />Criada em {{ formatDate(showcase.criado_em) }}</span>
              <span>Expira em {{ formatDate(showcase.expira_em) }}</span>
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <template v-if="showcase.status === 'ativa' && showcase.link_publico">
              <button class="inline-flex items-center gap-2 rounded-xl border border-line px-3 py-2 text-sm font-semibold text-purple hover:bg-cream" @click="copyLink(showcase)"><Copy :size="16" />Copiar link</button>
              <button class="inline-flex items-center gap-2 rounded-xl bg-[#25D366] px-3 py-2 text-sm font-semibold text-white hover:bg-[#20bd5a]" @click="share(showcase)"><MessageCircle :size="17" />WhatsApp</button>
              <button class="inline-flex items-center gap-2 rounded-xl border border-amber-200 px-3 py-2 text-sm font-semibold text-amber-700 hover:bg-amber-50" @click="requestAction(showcase, 'deactivate')"><Power :size="16" />Desativar</button>
            </template>
            <button v-else class="inline-flex items-center gap-2 rounded-xl border border-red-200 px-3 py-2 text-sm font-semibold text-red-600 hover:bg-red-50" @click="requestAction(showcase, 'delete')"><Trash2 :size="16" />Excluir permanentemente</button>
          </div>
        </div>
      </article>
    </div>

    <button v-if="error && !loading" class="primary-button mt-5" @click="loadShowcases"><RefreshCw :size="18" />Tentar novamente</button>
  </section>

  <ShowcaseActionModal v-if="target && action" :title="modalTitle" :description="modalDescription" :destructive="action === 'delete'" :loading="actionLoading" :error="actionError" @cancel="closeAction" @confirm="confirmAction" />
</template>
