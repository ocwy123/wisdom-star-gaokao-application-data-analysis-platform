import service from './index'

export function getStatistics() {
  return service.get('/overview/statistics')
}

export function getSchoolRank(params) {
  return service.get('/overview/school-rank', { params })
}

export function getMajorRank(params) {
  return service.get('/overview/major-rank', { params })
}

export function getScoreTrend(params) {
  return service.get('/overview/score-trend', { params })
}

export function getProvinceDifficulty(params) {
  return service.get('/overview/province-difficulty', { params })
}

export function getPlanDistribution(params) {
  return service.get('/overview/plan-distribution', { params })
}
