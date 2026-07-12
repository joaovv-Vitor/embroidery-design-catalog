<script setup lang="ts">
import {Star,ImageOff} from 'lucide-vue-next';
import type{DesenhoCard}from '@/types/api';
import{apiAssetUrl}from '@/services/api';
defineProps<{design:DesenhoCard}>();
defineEmits<{open:[id:number];favorite:[design:DesenhoCard]}>();
</script>
<template><article class="group cursor-pointer overflow-hidden rounded-[18px] border border-line bg-white shadow-sm transition duration-200 hover:-translate-y-1 hover:shadow-soft" tabindex="0" @click="$emit('open',design.id)" @keydown.enter="$emit('open',design.id)"><div class="relative aspect-square bg-cream p-5"><img v-if="design.preview_url" :src="apiAssetUrl(design.preview_url)!" :alt="`Preview de ${design.nome}`" class="h-full w-full object-contain"/><div v-else class="flex h-full items-center justify-center text-muted"><ImageOff :size="32"/></div><button :aria-label="design.favorito?'Remover favorito':'Adicionar favorito'" class="absolute right-3 top-3 rounded-full bg-white/95 p-2 shadow-sm" @click.stop="$emit('favorite',design)"><Star :size="20" :class="design.favorito?'fill-gold text-gold':'text-muted'"/></button></div><div class="p-4"><h2 class="truncate font-semibold text-purple">{{design.nome}}</h2><span v-if="design.categoria" class="mt-3 inline-block rounded-full bg-[#EDF3ED] px-3 py-1 text-xs font-medium text-sage">{{design.categoria.nome}}</span><span v-else class="mt-3 block text-xs text-muted">Sem categoria</span></div></article></template>
