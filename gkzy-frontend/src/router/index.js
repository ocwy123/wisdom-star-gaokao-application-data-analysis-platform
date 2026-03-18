import { createRouter, createWebHistory } from 'vue-router'
import SchoolList from '../views/SchoolList.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: SchoolList
  }
  // 如果有其他路由，可以继续添加
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router