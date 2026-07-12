import {createRouter,createWebHistory} from 'vue-router'
import CatalogView from '@/views/CatalogView.vue'; import ImportView from '@/views/ImportView.vue'; import ComingSoonView from '@/views/ComingSoonView.vue'
export default createRouter({history:createWebHistory(),routes:[{path:'/',component:CatalogView},{path:'/importar',component:ImportView},{path:'/categorias',component:ComingSoonView,props:{title:'Categorias'}},{path:'/lixeira',component:ComingSoonView,props:{title:'Lixeira'}}]})
