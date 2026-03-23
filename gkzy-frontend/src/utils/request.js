import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 10000
})

request.interceptors.request.use(
  config => {
    // 优先使用用户token，如果没有则使用管理员token
    const userToken = localStorage.getItem('userToken')
    const adminToken = localStorage.getItem('adminToken')
    const token = userToken || adminToken
    
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

request.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 检查是否是管理员还是用户
          const isAdminPath = window.location.pathname.startsWith('/admin')
          if (isAdminPath) {
            localStorage.removeItem('adminToken')
            localStorage.removeItem('adminInfo')
            if (window.location.pathname !== '/admin/login') {
              ElMessage.error('登录已过期，请重新登录')
              window.location.href = '/admin/login'
            }
          } else {
            localStorage.removeItem('userToken')
            localStorage.removeItem('userInfo')
            if (window.location.pathname !== '/login') {
              ElMessage.error('登录已过期，请重新登录')
              window.location.href = '/login'
            }
          }
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(error.response.data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败，请检查后端服务是否启动')
    }
    return Promise.reject(error)
  }
)

export default request