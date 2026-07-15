<script setup lang="ts">
import { AlertTriangle, Power, Trash2, X } from 'lucide-vue-next'

import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

defineProps<{ title: string; description: string; destructive?: boolean; loading?: boolean; error?: string }>()
defineEmits<{ cancel: []; confirm: [] }>()
</script>

<template>
  <div class="fixed inset-0 z-[80] flex items-center justify-center bg-ink/70 p-4 backdrop-blur-sm" role="alertdialog" aria-modal="true" aria-labelledby="showcase-action-title" @click.self="!loading && $emit('cancel')">
    <div class="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl sm:p-8">
      <div class="flex items-start justify-between">
        <span :class="['rounded-2xl p-3', destructive ? 'bg-red-50 text-red-600' : 'bg-amber-50 text-amber-700']"><AlertTriangle :size="28" /></span>
        <button class="rounded-full border border-line p-2 text-muted" :disabled="loading" aria-label="Cancelar" @click="$emit('cancel')"><X /></button>
      </div>
      <h2 id="showcase-action-title" class="mt-5 font-serif text-3xl text-purple">{{ title }}</h2>
      <p class="mt-3 text-sm leading-6 text-muted">{{ description }}</p>
      <p v-if="error" class="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700" role="alert">{{ error }}</p>
      <div class="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <button class="rounded-xl border border-line px-5 py-3 font-semibold text-purple" :disabled="loading" @click="$emit('cancel')">Cancelar</button>
        <button :class="['inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 font-semibold text-white disabled:opacity-60', destructive ? 'bg-red-600 hover:bg-red-700' : 'bg-terracotta hover:bg-[#c85f40]']" :disabled="loading" @click="$emit('confirm')">
          <LoadingSpinner v-if="loading" />
          <Trash2 v-else-if="destructive" :size="18" />
          <Power v-else :size="18" />
          {{ loading ? 'Aguarde…' : destructive ? 'Excluir permanentemente' : 'Desativar vitrine' }}
        </button>
      </div>
    </div>
  </div>
</template>
