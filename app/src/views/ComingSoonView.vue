<script setup lang="ts">
import{Construction}from'lucide-vue-next';
defineProps<{title:string}>();
</script>
<template><section class="mx-auto max-w-4xl"><h1 class="font-serif text-4xl text-purple md:text-5xl">{{title}}</h1><div class="mt-9 rounded-3xl border border-line bg-white p-12 text-center"><Construction class="mx-auto text-sage" :size="46"/><p class="mt-5 text-muted">Esta funcionalidade será adicionada em breve.</p></div></section></template>
