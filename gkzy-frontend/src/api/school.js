import request from '../utils/request'

// 打印API调用信息
const logApiCall = (url, method, params) => {
  console.log(`API Call: ${method} ${url}`, params)
}

/**
 * 获取高校列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.province - 省份
 * @param {string} params.city - 城市
 * @param {string} params.type - 学校类型
 * @param {boolean} params.is_985 - 是否 985
 * @param {boolean} params.is_211 - 是否 211
 * @param {boolean} params.is_double_first - 是否双一流
 * @param {string} params.keyword - 搜索关键词
 */
export function getSchoolList(params) {
  return request({
    url: '/school/list',
    method: 'get',
    params
  })
}

/**
 * 获取高校详情
 * @param {number} id - 学校 ID
 */
export function getSchoolDetail(id) {
  const url = `/school/detail/${id}`
  logApiCall(url, 'GET')
  return request({
    url,
    method: 'get'
  })
}

/**
 * 获取所有省份列表
 */
export function getProvinces() {
  return request({
    url: '/school/provinces',
    method: 'get'
  })
}

/**
 * 获取所有城市列表
 * @param {string} province - 省份（可选）
 */
export function getCities(province) {
  return request({
    url: '/school/cities',
    method: 'get',
    params: { province }
  })
}

/**
 * 获取所有学校类型列表
 */
export function getSchoolTypes() {
  return request({
    url: '/school/types',
    method: 'get'
  })
}

/**
 * 获取学校招生省份列表
 * @param {number} schoolId - 学校 ID
 */
export function getSchoolProvinces(schoolId) {
  return request({
    url: `/school/${schoolId}/provinces`,
    method: 'get'
  })
}

/**
 * 获取学校在指定省份的专业列表
 * @param {number} schoolId - 学校 ID
 * @param {string} province - 省份
 */
export function getSchoolMajors(schoolId, province) {
  return request({
    url: `/school/${schoolId}/majors`,
    method: 'get',
    params: { province }
  })
}

/**
 * 获取学校专业分数线数据
 * @param {number} schoolId - 学校 ID
 * @param {string} province - 省份
 * @param {string} major - 专业
 */
export function getAdmissionScores(schoolId, province, major) {
  return request({
    url: `/school/${schoolId}/scores`,
    method: 'get',
    params: { province, major }
  })
}