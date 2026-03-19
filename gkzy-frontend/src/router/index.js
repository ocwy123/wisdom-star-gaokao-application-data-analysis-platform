import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import SchoolList from '../views/SchoolList.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/schools',
    name: 'SchoolList',
    component: SchoolList
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router