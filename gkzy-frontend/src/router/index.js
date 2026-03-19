import { createRouter, createWebHistory } from 'vue-router'
import SchoolList from '../views/SchoolList.vue'
import MajorDetail from '../views/MajorDetail.vue'

const routes = [
  {path: '/', name: 'Home', component: SchoolList},
  {path: '/major/:id', name: 'MajorDetail', component: MajorDetail, props: true,}
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router