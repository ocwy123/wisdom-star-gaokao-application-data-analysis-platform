import service from './index'

export function getSchoolList(params) {
  return service.get('/school/list', { params })
}

export function getSchoolDetail(id) {
  return service.get(`/school/detail/${id}`)
}