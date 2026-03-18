import service from './index'

export function getSchoolHeat() {
  return service.get('/heat/school')
}