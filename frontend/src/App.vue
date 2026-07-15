<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import AppSidebar from '@/components/layout/AppSidebar.vue'

const route = useRoute()
const publicPage = computed(() => route.meta.public === true)
</script>

<template>
  <router-view v-if="publicPage" />
  <div v-else class="min-h-screen">
    <AppSidebar />
    <main class="min-h-screen px-5 pb-12 pt-20 md:ml-60 md:px-8 md:pt-10 xl:px-12">
      <router-view />
    </main>
  </div>
</template>
