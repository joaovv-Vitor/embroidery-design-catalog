<script setup lang="ts">
import { CheckCircle2, Copy, MessageCircle, X } from 'lucide-vue-next'

import type { VitrineCriada } from '@/types/api'

defineProps<{ showcase: VitrineCriada; feedback?: string }>()
defineEmits<{ close: []; copy: []; whatsapp: [] }>()
</script>

<template>
  <div class="fixed inset-0 z-[80] flex items-center justify-center bg-ink/70 p-4 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="showcase-success-title">
    <div class="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl sm:p-8">
      <div class="flex items-start justify-between">
        <span class="rounded-2xl bg-green-50 p-3 text-green-700"><CheckCircle2 :size="30" /></span>
        <button class="rounded-full border border-line p-2 text-muted" aria-label="Fechar" @click="$emit('close')"><X /></button>
      </div>
      <h2 id="showcase-success-title" class="mt-5 font-serif text-3xl text-purple">Vitrine criada!</h2>
      <p class="mt-2 text-sm leading-6 text-muted"><strong class="text-ink">{{ showcase.titulo }}</strong> está disponível por sete dias e pronta para ser enviada.</p>
      <div class="mt-5 break-all rounded-xl border border-line bg-cream p-4 text-sm text-purple">{{ showcase.link_publico }}</div>
      <p v-if="feedback" class="mt-3 text-sm font-medium text-sage" role="status">{{ feedback }}</p>
      <div class="mt-6 grid gap-3 sm:grid-cols-2">
        <button class="inline-flex items-center justify-center gap-2 rounded-xl border border-line px-4 py-3 font-semibold text-purple hover:bg-cream" @click="$emit('copy')"><Copy :size="18" />Copiar link</button>
        <button class="inline-flex items-center justify-center gap-2 rounded-xl bg-[#25D366] px-4 py-3 font-semibold text-white hover:bg-[#20bd5a]" @click="$emit('whatsapp')"><MessageCircle :size="19" />Compartilhar</button>
      </div>
    </div>
  </div>
</template>
