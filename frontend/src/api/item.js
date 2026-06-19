import request from '@/utils/request'

// 获取物品列表
export function getItems(params) {
  return request({
    url: '/items/',
    method: 'get',
    params
  })
}

// 获取物品详情
export function getItemById(id) {
  return request({
    url: `/items/${id}`,
    method: 'get'
  })
}

// 创建物品
export function createItem(data) {
  return request({
    url: '/items/',
    method: 'post',
    data
  })
}

// 更新物品
export function updateItem(id, data) {
  return request({
    url: `/items/${id}`,
    method: 'put',
    data
  })
}

// 删除物品
export function deleteItem(id) {
  return request({
    url: `/items/${id}`,
    method: 'delete'
  })
}

// 获取所有标签
export function getAllTags(params) {
  return request({
    url: '/items/tags/all',
    method: 'get',
    params
  })
}

// 获取单个标签详情
export function getTagById(id) {
  return request({
    url: `/items/tags/${id}`,
    method: 'get'
  })
}

// 创建标签（仅管理员）
export function createTag(data) {
  return request({
    url: '/items/tags/',
    method: 'post',
    data
  })
}

// 更新标签（仅管理员）
export function updateTag(id, data) {
  return request({
    url: `/items/tags/${id}`,
    method: 'put',
    data
  })
}

// 删除标签（仅管理员）
export function deleteTag(id) {
  return request({
    url: `/items/tags/${id}`,
    method: 'delete'
  })
}

// 搜索物品
export function searchItems(query, limit = null) {
  const params = { q: query }
  if (limit !== null && limit !== undefined) {
    params.limit = limit
  }
  return request({
    url: '/items/search',
    method: 'get',
    params: params
  })
}