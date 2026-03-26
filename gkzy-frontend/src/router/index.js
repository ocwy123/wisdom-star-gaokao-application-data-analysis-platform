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
    path: '/school/:id',
    name: 'SchoolDetail',
    component: SchoolDetail,
    props: true
  },
  {
    path: '/faq',
    name: 'FaqDetail',
    component: () => import('../views/FaqDetail.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  console.log('路由守卫: 从', from.path, '到', to.path)
  const adminToken = localStorage.getItem('adminToken')
  const userToken = localStorage.getItem('userToken')
  
  console.log('Token状态 - adminToken:', adminToken, 'userToken:', userToken)
  
  // 管理员路由检查
  if (to.meta.adminOnly) {
    console.log('管理员路由检查')
    if (to.meta.requiresAuth && !adminToken) {
      console.log('需要管理员认证，跳转到管理员登录')
      next('/admin/login')
    } else if (to.meta.requiresGuest && adminToken) {
      console.log('管理员已登录，跳转到管理员仪表板')
      next('/admin/dashboard')
    } else {
      console.log('管理员路由检查通过')
      next()
    }
    return
  }
  
  // 普通用户路由检查
  console.log('普通用户路由检查')
  
  // 特殊处理：允许已登录用户访问注册页面
  if (to.path === '/register' && userToken) {
    console.log('允许已登录用户访问注册页面')
    next()
    return
  }
  
  if (to.meta.requiresAuth && !userToken) {
    console.log('需要用户认证，跳转到登录页面')
    next('/login')
  } else if (to.meta.requiresGuest && userToken && to.path !== '/register') {
    console.log('用户已登录，跳转到首页')
    next('/')
  } else {
    console.log('普通用户路由检查通过')
    next()
  }
})

export default router