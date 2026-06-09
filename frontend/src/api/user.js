import request from '@/utils/request'

// 获取用户列表
export function getUsers(params) {
  return request({
    url: '/auth/users',
    method: 'get',
    params
  })
}

// 更新用户状态
export function updateUserStatus(userId, data) {
  return request({
    url: `/auth/users/${userId}/status`,
    method: 'put',
    data
  })
}
