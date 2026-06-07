import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref(null)
  const token = ref(localStorage.getItem('access_token') || '')

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
      localStorage.setItem('access_token', res.access_token)
      localStorage.setItem('refresh_token', res.refresh_token)
      userInfo.value = res.user
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

  // 获取用户信息
  async function getUserInfo() {
    try {
      // TODO: 实现获取用户信息API
      return userInfo.value
    } catch (error) {
      throw error
    }
  }

  // 登出
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/login')
  }

  return {
    userInfo,
    token,
    isAdmin,
    isLoggedIn,
    login,
    register,
    getUserInfo,
    logout
  }
})
