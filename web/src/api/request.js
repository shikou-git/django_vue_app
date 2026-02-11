/**
 * Axios 实例：baseURL、请求头携带 Token、响应统一解包与 401 处理
 */
import axios from 'axios'
import router from '../router'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/auth'

const request = axios.create({
  baseURL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截：携带 Access Token（登录/刷新接口不需要，由调用方不传或跳过）
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：解包 { code, msg, data }，401 跳转登录
request.interceptors.response.use(
  (response) => {
    const { data } = response
    if (data && typeof data.code !== 'undefined' && data.code !== 0 && data.code !== 200) {
      return Promise.reject(new Error(data.msg || '请求失败'))
    }
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      router.push('/login')
    }
    const msg = error.response?.data?.msg || error.message || '网络错误'
    return Promise.reject(new Error(msg))
  }
)

export default request
