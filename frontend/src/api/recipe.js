import request from '@/utils/request'

// 获取配方列表
export function getRecipes(params) {
  return request({
    url: '/recipes/',
    method: 'get',
    params
  })
}

// 获取配方详情
export function getRecipeById(id) {
  return request({
    url: `/recipes/${id}`,
    method: 'get'
  })
}

// 创建配方
export function createRecipe(data) {
  return request({
    url: '/recipes/',
    method: 'post',
    data
  })
}

// 更新配方（仅管理员）
export function updateRecipe(id, data) {
  return request({
    url: `/recipes/${id}`,
    method: 'put',
    data
  })
}

// 删除配方（仅管理员）
export function deleteRecipe(id) {
  return request({
    url: `/recipes/${id}`,
    method: 'delete'
  })
}
