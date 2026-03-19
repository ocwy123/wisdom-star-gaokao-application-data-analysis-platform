import { createRouter, createWebHistory } from 'vue-router'
<<<<<<< HEAD
=======
import Dashboard from '../views/Dashboard.vue'
>>>>>>> d542ff691db917f1a695eec4809a16ccd8426862
import SchoolList from '../views/SchoolList.vue'

const routes = [
  {
    path: '/',
<<<<<<< HEAD
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
=======
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/schools',
    name: 'SchoolList',
    component: SchoolList
>>>>>>> d542ff691db917f1a695eec4809a16ccd8426862
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

<<<<<<< HEAD
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

=======
>>>>>>> d542ff691db917f1a695eec4809a16ccd8426862
export default router