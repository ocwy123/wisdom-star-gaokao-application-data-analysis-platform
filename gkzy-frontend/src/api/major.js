import service from './index'

/**
 * 获取专业列表
 * @param {Object} params - 查询参数 {page, size, keyword}
 * @returns {Promise}
 */
export function getMajorList(params) {
  return service.get('/major/list', { params })
}

/**
 * 获取专业详情
 * @param {Number} majorId - 专业ID
 * @returns {Promise}
 */
export function getMajorDetail(majorId) {
  return service.get(`/major/${majorId}`)
}

/**
 * 获取专业就业数据
 * @param {Number} majorId - 专业ID
 * @param {Number} year - 年份(可选)
 * @returns {Promise}
 */
export function getMajorEmployment(majorId, year) {
  const params = year ? { year } : {}
  return service.get(`/major/${majorId}/employment`, { params })
}

/**
 * 获取开设该专业的高校列表
 * @param {Number} majorId - 专业ID
 * @param {Object} params - 分页参数 {page, size}
 * @returns {Promise}
 */
export function getMajorSchools(majorId, params) {
  return service.get(`/major/${majorId}/schools`, { params })
}

/**
 * 获取专业深度分析数据
 * @param {Number} majorId - 专业ID
 * @returns {Promise}
 */
export function getMajorAnalysis(majorId) {
  return service.get(`/major/${majorId}/analysis`)
}