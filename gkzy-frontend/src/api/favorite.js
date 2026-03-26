import request from './index'

// 添加收藏
export const addFavorite = (data) => {
  return request({
    url: '/favorite/add',
    method: 'POST',
    data
  })
}

// 取消收藏
export const removeFavorite = (data) => {
  return request({
    url: '/favorite/remove',
    method: 'POST',
    data
  })
}

// 获取收藏列表
export const getFavorites = (params) => {
  return request({
    url: '/favorite/list',
    method: 'GET',
    params
  })
}

// 检查是否已收藏
export const checkFavorite = (params) => {
  return request({
    url: '/favorite/check',
    method: 'GET',
    params
  })
}