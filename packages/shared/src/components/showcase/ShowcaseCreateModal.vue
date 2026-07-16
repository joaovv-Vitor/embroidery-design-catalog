<script setup lang="ts">
import { ImageOff, Send, X } from 'lucide-vue-next'
import { ref } from 'vue'

import type { DesenhoCard } from '@catalogo-bordados/shared'
import { apiAssetUrl } from '@catalogo-runtime/services/api'

import LoadingSpinner from '../ui/LoadingSpinner.vue'

defineProps<{
  designs: DesenhoCard[]
  loading?: boolean
  error?: string
}>()

const emit = defineEmits<{
  close: []
  remove: [id: number]
  create: [data: { titulo?: string; nome_cliente?: string | null }]
}>()

const title = ref('')
const clientName = ref('')

function submit(): void {
  emit('create', {
    titulo: title.value.trim() || undefined,
    nome_cliente: clientName.value.trim() || null,
  })
}
</script>

<template>
  <div
    class="fixed inset-0 z-[80] flex items-center justify-center bg-ink/70 p-4 backdrop-blur-sm"
    role="dialog"
    aria-modal="true"
    aria-labelledby="showcase-create-title"
    @click.self="!loading && $emit('close')"
  >
    <form class="flex max-h-[92vh] w-full max-w-2xl flex-col rounded-3xl bg-white shadow-2xl" @submit.prevent="submit">
      <header class="flex items-start justify-between gap-4 border-b border-line p-6 sm:p-8">
        <div>
          <h2 id="showcase-create-title" class="font-serif text-3xl text-purple">Criar vitrine</h2>
          <p class="mt-1 text-sm text-muted">Revise os desenhos e personalize a apresentação para o cliente.</p>
        </div>
        <button type="button" class="rounded-full border border-line p-2 text-muted" :disabled="loading" aria-label="Fechar" @click="$emit('close')">
          <X />
        </button>
      </header>

      <div class="overflow-y-auto p-6 sm:p-8">
        <div class="grid gap-4 sm:grid-cols-2">
          <label class="block text-sm font-medium text-purple">
            Título <span class="font-normal text-muted">(opcional)</span>
            <input v-model="title" class="field mt-2" maxlength="255" placeholder="Opções de bordado" :disabled="loading" />
          </label>
          <label class="block text-sm font-medium text-purple">
            Nome do cliente <span class="font-normal text-muted">(opcional)</span>
            <input v-model="clientName" class="field mt-2" maxlength="255" placeholder="Ex.: Maria" :disabled="loading" />
          </label>
        </div>

        <div class="mt-7 flex items-center justify-between">
          <h3 class="font-semibold text-purple">{{ designs.length }} {{ designs.length === 1 ? 'desenho selecionado' : 'desenhos selecionados' }}</h3>
          <span class="text-xs text-muted">Validade: 7 dias</span>
        </div>

        <ul class="mt-3 space-y-2">
          <li v-for="design in designs" :key="design.id" class="flex items-center gap-3 rounded-xl border border-line p-2">
            <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-cream p-1">
              <img v-if="design.preview_url" :src="apiAssetUrl(design.preview_url)!" :alt="`Preview de ${design.nome}`" class="h-full w-full object-contain" />
              <ImageOff v-else :size="20" class="text-muted" />
            </div>
            <span class="min-w-0 flex-1 truncate text-sm font-medium text-purple">{{ design.nome }}</span>
            <button type="button" class="rounded-full p-2 text-muted hover:bg-red-50 hover:text-red-600" :aria-label="`Remover ${design.nome} da seleção`" :disabled="loading" @click="$emit('remove', design.id)">
              <X :size="18" />
            </button>
          </li>
        </ul>

        <p v-if="!designs.length" class="mt-4 rounded-xl bg-amber-50 p-4 text-sm text-amber-800">Selecione pelo menos um desenho para criar a vitrine.</p>
        <p v-if="error" class="mt-4 rounded-xl bg-red-50 p-4 text-sm text-red-700" role="alert">{{ error }}</p>
      </div>

      <footer class="flex flex-col-reverse gap-3 border-t border-line p-6 sm:flex-row sm:justify-end sm:px-8">
        <button type="button" class="rounded-xl border border-line px-5 py-3 font-semibold text-purple" :disabled="loading" @click="$emit('close')">Cancelar</button>
        <button class="primary-button" :disabled="loading || !designs.length">
          <LoadingSpinner v-if="loading" />
          <Send v-else :size="18" />
          {{ loading ? 'Criando…' : `Criar vitrine com ${designs.length} ${designs.length === 1 ? 'desenho' : 'desenhos'}` }}
        </button>
      </footer>
    </form>
  </div>
</template>
