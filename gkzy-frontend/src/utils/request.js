import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 20000
})

request.interceptors.request.use(
  config => {
    // 根据当前路径决定使用哪种token
    const isAdminPath = config.url?.startsWith('/admin') || window.location.pathname.startsWith('/admin')
    
    if (isAdminPath) {
      // 管理员路径：只使用管理员token
      const adminToken = localStorage.getItem('adminToken')
      if (adminToken) {
        config.headers['Authorization'] = `Bearer ${adminToken}`
      }
    } else {
      // 普通用户路径：使用用户token
      const userToken = localStorage.getItem('userToken')
      if (userToken) {
        config.headers['Authorization'] = `Bearer ${userToken}`
      }
    }
    
    return config
  },
  error => Promise.reject(error)
)

request.interceptors.response.use(
  response => {
    console.log('Response received:', response)
    return response
  },
  error => {
    console.error('Response error:', error)
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 检查是否是管理员还是用户
          const isAdminPath = window.location.pathname.startsWith('/admin')
          if (isAdminPath) {
            // 只有在当前页面不是登录页时才跳转，避免循环跳转
            if (window.location.pathname !== '/admin/login') {
              localStorage.removeItem('adminToken')
              localStorage.removeItem('adminInfo')
              ElMessage.error('登录已过期，请重新登录')
              window.location.href = '/admin/login'
            }
          } else {
            // 只有在当前页面不是登录页时才跳转，避免循环跳转
            if (window.location.pathname !== '/login') {
              localStorage.removeItem('userToken')
              localStorage.removeItem('userInfo')
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