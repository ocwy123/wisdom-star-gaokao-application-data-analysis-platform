import service from './index'

/**
 * 获取高校热度排行
 * @returns {Promise}
 */
export function getSchoolHeat() {
  return service.get('/heat/school')
}

// /**
//  * 获取专业热度排行
//  * @returns {Promise}
//  */
// export function getMajorHeat() {
//   return service.get('/heat/major')  // 假设后端有这个接口
// }