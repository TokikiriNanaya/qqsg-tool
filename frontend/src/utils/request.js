import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 检查是否配置了静默错误
    const silentError = error.config?.silentError
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          if (!silentError) {
            ElMessage.error('未授权，请登录')
          }
          // 清除token，但不在此处跳转，由路由守卫处理
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user_info')
          break
        case 403:
          if (!silentError) {
            ElMessage.error('权限不足')
          }
          break
        case 404:
          if (!silentError) {
            ElMessage.error('请求的资源不存在')
          }
          break
        case 500:
          if (!silentError) {
            ElMessage.error('服务器错误')
          }
          break
        default:
          if (!silentError) {
            ElMessage.error(error.response.data.detail || '请求失败')
          }
      }
    } else {
      if (!silentError) {
        ElMessage.error('网络错误')
      }
    }
    return Promise.reject(error)
  }
)

export default request
