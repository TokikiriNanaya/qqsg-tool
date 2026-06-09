import request from '@/utils/request'

// 获取当前用户信息
export function getCurrentUser(silent = false) {
  return request({
    url: '/auth/me',
    method: 'get',
    silentError: silent  // 支持静默错误
  })
}

// 登录
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

// 注册
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}
