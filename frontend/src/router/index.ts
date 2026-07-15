import { createRouter, createWebHistory } from 'vue-router'

import CatalogView from '@/views/CatalogView.vue'
import CategoriesView from '@/views/CategoriesView.vue'
import ImportView from '@/views/ImportView.vue'
import PublicShowcaseView from '@/views/PublicShowcaseView.vue'
import SharedShowcasesView from '@/views/SharedShowcasesView.vue'
import TrashView from '@/views/TrashView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: CatalogView },
    { path: '/importar', component: ImportView },
    { path: '/categorias', component: CategoriesView },
    { path: '/lixeira', component: TrashView },
    { path: '/vitrines', component: SharedShowcasesView },
    { path: '/vitrines/:token', component: PublicShowcaseView, meta: { public: true } },
  ],
})
