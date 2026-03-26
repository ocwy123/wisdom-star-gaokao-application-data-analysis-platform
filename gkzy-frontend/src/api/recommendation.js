import request from '../utils/request'

/**
 * 获取志愿推荐
 * @param {Object} data - 推荐参数
 * @param {number} data.score - 高考分数
 * @param {string} data.province - 用户所在省份
 * @param {string} data.subject - 选科类别 (物理类、历史类、理科、文科、综合类)
 * @param {string} data.school_province - 可选，理想院校省份
 * @param {string} data.school_type - 可选，理想院校类型
 */
export function getVolunteerRecommendation(data) {
  return request({
    url: '/recommendation/volunteer',
    method: 'post',
    data
  })
}