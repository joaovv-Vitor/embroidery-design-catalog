<script setup lang="ts">
import { AlertTriangle, Trash2, X } from 'lucide-vue-next'

import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

defineProps<{
  designName: string
  permanent?: boolean
  loading?: boolean
  error?: string
}>()

defineEmits<{
  cancel: []
  confirm: []
}>()
</script>

<template>
  <div
    class="fixed inset-0 z-[80] flex items-center justify-center bg-ink/70 p-4 backdrop-blur-sm"
    role="alertdialog"
    aria-modal="true"
    aria-labelledby="removal-title"
    @click.self="!loading && $emit('cancel')"
  >
    <div class="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl sm:p-8">
      <div class="flex items-start justify-between gap-4">
        <span class="rounded-2xl bg-red-50 p-3 text-red-600">
          <AlertTriangle :size="28" />
        </span>
        <button
          type="button"
          class="rounded-full border border-line p-2 text-muted"
          aria-label="Cancelar remoção"
          :disabled="loading"
          @click="$emit('cancel')"
        >
          <X />
        </button>
      </div>

      <h2 id="removal-title" class="mt-5 font-serif text-3xl text-purple">
        {{ permanent ? 'Excluir permanentemente?' : 'Mover para a lixeira?' }}
      </h2>
      <p class="mt-3 text-sm leading-6 text-muted">
        <strong class="text-ink">{{ designName }}</strong>
        {{ permanent
          ? 'será removido definitivamente, incluindo preview e arquivos de backup.'
          : 'será removido do catálogo e poderá ser recuperado durante o período de retenção.' }}
      </p>

      <div class="mt-5 rounded-xl bg-amber-50 p-4 text-sm text-amber-800">
        Esta ação não altera cópias existentes em pendrives, computadores ou outros dispositivos físicos.
      </div>

      <p v-if="error" class="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700" role="alert">
        {{ error }}
      </p>

      <div class="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <button
          type="button"
          class="rounded-xl border border-line px-5 py-3 font-semibold text-purple"
          :disabled="loading"
          @click="$emit('cancel')"
        >
          Cancelar
        </button>
        <button
          type="button"
          class="inline-flex items-center justify-center gap-2 rounded-xl bg-red-600 px-5 py-3 font-semibold text-white transition hover:bg-red-700 disabled:opacity-60"
          :disabled="loading"
          @click="$emit('confirm')"
        >
          <LoadingSpinner v-if="loading" />
          <Trash2 v-else :size="18" />
          {{ loading ? 'Removendo…' : permanent ? 'Excluir definitivamente' : 'Mover para lixeira' }}
        </button>
      </div>
    </div>
  </div>
</template>
