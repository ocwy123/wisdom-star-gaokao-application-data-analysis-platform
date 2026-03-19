import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import SchoolList from '../views/SchoolList.vue'
import MajorDetail from '../views/MajorDetail.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: SchoolList
  },
  // 管理员路由
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/admin/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/admin/register',
    name: 'AdminRegister',
    component: () => import('../views/admin/Register.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('../views/admin/AdminDashboard.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('adminToken')
  
  if (to.meta.requiresAuth && !token) {
    next('/admin/login')
  } else if (to.meta.requiresGuest && token) {
    next('/admin/dashboard')
  } else {
    next()
  }
})

export default router