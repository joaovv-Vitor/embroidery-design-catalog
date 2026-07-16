<script setup lang="ts">
import AppSidebar from '@catalogo-bordados/shared/components/layout/AppSidebar.vue'
</script>

<template>
  <div class="min-h-screen">
    <AppSidebar />
    <main class="min-h-screen px-5 pb-12 pt-20 md:ml-60 md:px-8 md:pt-10 xl:px-12">
      <router-view />
    </main>
  </div>
</template>
