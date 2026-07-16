import { createRouter, createWebHistory } from 'vue-router'

import CatalogView from '@catalogo-bordados/shared/views/CatalogView.vue'
import CategoriesView from '@catalogo-bordados/shared/views/CategoriesView.vue'
import SharedShowcasesView from '@catalogo-bordados/shared/views/SharedShowcasesView.vue'
import TrashView from '@catalogo-bordados/shared/views/TrashView.vue'

import ImportView from '@/views/ImportView.vue'
import PublicShowcaseView from '@/views/PublicShowcaseView.vue'

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
