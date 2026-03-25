import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import SchoolList from '../views/SchoolList.vue'
import MajorList from '../views/MajorList.vue'
import MajorDetail from '../views/MajorDetail.vue'
import SchoolDetail from '../views/SchoolDetail.vue'  // 新增

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  // 用户认证路由
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  // 高校相关路由
  {
    path: '/schools',
    name: 'SchoolList',
    component: SchoolList
  },
    {
    path: '/school/:id',
    name: 'SchoolDetail',
    component: SchoolDetail,
    props: true
  },
  // 专业相关路由
  {
    path: '/majors',
    name: 'MajorList',
    component: MajorList
  },
  {
    path: '/major/:id',
    name: 'MajorDetail',
    component: MajorDetail,
    props: true
  },
  {
    path: '/analysis/deep-search',
    name: 'DeepSearch',
    component: () => import('../views/analysis/DeepSearch.vue')
  },
  {
    path: '/analysis/multi-dimension',
    name: 'MultiDimensionAnalysis',
    component: () => import('../views/analysis/MultiDimensionAnalysis.vue')
  },
  // 管理员路由
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/admin/Login.vue'),
    meta: { requiresGuest: true, adminOnly: true }
  },
  {
    path: '/admin/register',
    name: 'AdminRegister',
    component: () => import('../views/admin/Register.vue'),
    meta: { requiresGuest: true, adminOnly: true }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('../views/admin/AdminDashboard.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const adminToken = localStorage.getItem('adminToken')
  const userToken = localStorage.getItem('userToken')
  
  // 管理员路由检查
  if (to.meta.adminOnly) {
    if (to.meta.requiresAuth && !adminToken) {
      next('/admin/login')
    } else if (to.meta.requiresGuest && adminToken) {
      next('/admin/dashboard')
    } else {
      next()
    }
    return
  }
  
  // 普通用户路由检查
  if (to.meta.requiresAuth && !userToken) {
    next('/login')
  } else if (to.meta.requiresGuest && userToken) {
    next('/')
  } else {
    next()
  }
})

export default router