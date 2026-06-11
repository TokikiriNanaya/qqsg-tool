import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 标记是否正在刷新token
let isRefreshing = false
// 存储在token刷新期间等待的请求
let refreshSubscribers = []

// 添加请求到刷新队列
const subscribeTokenRefresh = (callback) => {
  refreshSubscribers.push(callback)
}

// 通知所有等待的请求token已刷新
const onTokenRefreshed = (token) => {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

// 刷新token
const refreshToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) {
    return null
  }
  
  try {
    const response = await axios.post('/api/auth/refresh', { refresh_token: refreshToken })
    const newToken = response.data.access_token
    localStorage.setItem('access_token', newToken)
    return newToken
  } catch (error) {
    console.error('Token刷新失败:', error)
    return null
  }
}

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
  async error => {
    // 检查是否配置了静默错误
    const silentError = error.config?.silentError
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 如果不是刷新token的请求，尝试刷新token
          if (!error.config.url.includes('/auth/refresh') && !error.config.url.includes('/auth/login')) {
            if (isRefreshing) {
              // 正在刷新，等待刷新完成后重试
              return new Promise((resolve, reject) => {
                subscribeTokenRefresh(token => {
                  error.config.headers.Authorization = `Bearer ${token}`
                  resolve(request(error.config))
                })
              })
            }
            
            isRefreshing = true
            const newToken = await refreshToken()
            
            if (newToken) {
              onTokenRefreshed(newToken)
              isRefreshing = false
              // 重试原请求
              error.config.headers.Authorization = `Bearer ${newToken}`
              return request(error.config)
            } else {
              isRefreshing = false
              if (!silentError) {
                ElMessage.error('登录已过期，请重新登录')
              }
              localStorage.removeItem('access_token')
              localStorage.removeItem('refresh_token')
              localStorage.removeItem('user_info')
              router.push('/login')
            }
          } else {
            // 刷新token的请求失败
            if (!silentError) {
              ElMessage.error('登录已过期，请重新登录')
            }
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('user_info')
            router.push('/login')
          }
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
