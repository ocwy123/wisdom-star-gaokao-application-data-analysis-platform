import axios from 'axios'

const service = axios.create({
  // baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  baseURL: 'http://localhost:5000/api',
  timeout: 10000
})

// 响应拦截器
service.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default service