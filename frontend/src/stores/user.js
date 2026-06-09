import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'
import router from '@/router'
import { getCurrentUser } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  
  // 安全地解析用户信息，避免JSON解析错误
  let storedUserInfo = null
  try {
    const userInfoStr = localStorage.getItem('user_info')
    if (userInfoStr) {
      storedUserInfo = JSON.parse(userInfoStr)
    }
  } catch (e) {
    console.error('解析用户信息失败:', e)
    localStorage.removeItem('user_info')
  }
  
  const userInfo = ref(storedUserInfo)

  const isAdmin = computed(() => {
    return userInfo.value?.role === 'admin'
  })

  const isLoggedIn = computed(() => {
    return !!token.value && !!userInfo.value
  })

  // 登录
  async function login(loginData) {
    try {
      const res = await request.post('/auth/login', loginData)
      token.value = res.access_token
      userInfo.value = res.user
      localStorage.setItem('access_token', res.access_token)
      localStorage.setItem('refresh_token', res.refresh_token)
      localStorage.setItem('user_info', JSON.stringify(res.user))
      router.push('/')
      return res
    } catch (error) {
      throw error
    }
  }

  // 注册
  async function register(registerData) {
    try {
      const res = await request.post('/auth/register', registerData)
      return res
    } catch (error) {
      throw error
    }
  }

  // 获取用户信息（从后端获取真实数据）
  async function fetchUserInfo(silent = false) {
    try {
      if (!token.value) {
        return null
      }
      const res = await getCurrentUser(silent)
      userInfo.value = res
      // 更新localStorage中的用户信息
      localStorage.setItem('user_info', JSON.stringify(res))
      return res
    } catch (error) {
      // 如果获取失败，说明token无效，清除登录状态
      console.error('获取用户信息失败:', error)
      // 不在这里调用logout，让调用方决定如何处理
      throw error
    }
  }

  // 初始化时验证用户身份
  async function initAuth() {
    if (token.value) {
      try {
        // 使用静默模式，不显示错误提示
        await fetchUserInfo(true)
        console.log('用户身份验证成功:', userInfo.value?.username)
      } catch (error) {
        // 初始化失败，清除无效的登录状态
        console.warn('用户身份验证失败，清除登录状态')
        token.value = ''
        userInfo.value = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user_info')
      }
    } else {
      console.log('未检测到token，用户未登录')
    }
  }

  // 登出
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
    router.push('/login')
  }

  return {
    userInfo,
    token,
    isAdmin,
    isLoggedIn,
    login,
    register,
    fetchUserInfo,
    initAuth,
    logout
  }
})
