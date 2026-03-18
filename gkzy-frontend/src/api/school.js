import service from './index'

export function getSchoolList(params) {
  return service.get('/school/list', { params })
}