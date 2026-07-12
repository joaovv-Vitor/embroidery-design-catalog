import { createRouter, createWebHistory } from 'vue-router'

import CatalogView from '@/views/CatalogView.vue'
import CategoriesView from '@/views/CategoriesView.vue'
import ImportView from '@/views/ImportView.vue'
import TrashView from '@/views/TrashView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: CatalogView },
    { path: '/importar', component: ImportView },
    { path: '/categorias', component: CategoriesView },
    { path: '/lixeira', component: TrashView },
  ],
})
