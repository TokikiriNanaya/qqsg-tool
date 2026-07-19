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

// ===== 字典接口 =====

// 获取指定类型的字典列表（公开，走缓存）
export function getDict(dictType) {
  return request({
    url: `/dict/${dictType}`,
    method: 'get'
  })
}

// 获取所有字典项（管理员）
export function getAllDicts(params) {
  return request({
    url: '/dict/',
    method: 'get',
    params
  })
}

// 创建字典项（管理员）
export function createDict(data) {
  return request({
    url: '/dict/',
    method: 'post',
    data
  })
}

// 更新字典项（管理员）
export function updateDict(id, data) {
  return request({
    url: `/dict/${id}`,
    method: 'put',
    data
  })
}

// 删除字典项（管理员）
export function deleteDict(id) {
  return request({
    url: `/dict/${id}`,
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