<template>
  <div class="compare-page">
    <Header />
    <div class="page-wrapper">
      <div class="hero-banner">
        <div class="hero-content">
          <h1 class="hero-title">多维对比分析</h1>
          <p class="hero-desc">数据驱动决策，深度对比学校、专业、地域与热度</p>
        </div>
      </div>

      <div class="main-container">
        <div class="config-panel">
          <div class="panel-header">
            <div class="step-indicators">
              <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
                <div class="step-circle">1</div>
                <span>维度</span>
              </div>
              <div class="step-line" :class="{ active: currentStep > 1 }"></div>
              <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
                <div class="step-circle">2</div>
                <span>对象</span>
              </div>
              <div class="step-line" :class="{ active: currentStep > 2 }"></div>
              <div class="step" :class="{ active: currentStep >= 3 }">
                <div class="step-circle">3</div>
                <span>指标</span>
              </div>
            </div>
          </div>

          <div class="panel-body">
            <div v-if="currentStep === 1" class="step-content">
              <h3 class="section-title">选择对比维度</h3>
              <div class="dimension-grid">
                <div v-for="dim in dimensions" :key="dim.value" class="dim-card"
                  :class="{ selected: form.dimension === dim.value }" @click="selectDimension(dim.value)">
                  <div class="dim-icon" :style="{ backgroundColor: dim.color }">
                    <el-icon :size="32" color="#fff">
                      <component :is="dim.icon" />
                    </el-icon>
                  </div>
                  <h4>{{ dim.label }}</h4>
                  <p>{{ dim.desc }}</p>
                </div>
              </div>
            </div>

            <div v-if="currentStep === 2" class="step-content">
              <h3 class="section-title">选择{{ getDimLabel(form.dimension) }}</h3>

              <div v-if="form.dimension === 'school'" class="selector-area">
                <div class="search-box">
                  <el-input v-model="schoolSearch" placeholder="搜索学校名称..." clearable prefix-icon="Search" />
                </div>
                <div class="tag-list">
                  <div v-for="opt in filteredSchools" :key="opt.key" class="tag-item"
                    :class="{ selected: form.schoolIds.includes(opt.key) }" @click="toggleSchool(opt.key)">
                    {{ opt.label }}
                  </div>
                </div>
                <div v-if="form.schoolIds.length > 0" class="selected-info">
                  已选 <strong>{{ form.schoolIds.length }}</strong> 所学校
                </div>
              </div>

              <div v-if="form.dimension === 'major'" class="selector-area">
                <div class="search-box">
                  <el-input v-model="majorSearch" placeholder="搜索专业名称..." clearable prefix-icon="Search" />
                </div>
                <div class="tag-list">
                  <div v-for="opt in filteredMajors" :key="opt.key" class="tag-item"
                    :class="{ selected: form.majorIds.includes(opt.key) }" @click="toggleMajor(opt.key)">
                    {{ opt.label }}
                  </div>
                </div>
                <div v-if="form.majorIds.length > 0" class="selected-info">
                  已选 <strong>{{ form.majorIds.length }}</strong> 个专业
                </div>
              </div>

              <div v-if="form.dimension === 'province'" class="selector-area">
                <div class="search-box">
                  <el-input v-model="provinceSearch" placeholder="搜索省份..." clearable prefix-icon="Search" />
                </div>
                <div class="tag-list">
                  <div v-for="opt in filteredProvinces" :key="opt.key" class="tag-item"
                    :class="{ selected: form.provinces.includes(opt.key) }" @click="toggleProvince(opt.key)">
                    {{ opt.label }}
                  </div>
                </div>
                <div v-if="form.provinces.length > 0" class="selected-info">
                  已选 <strong>{{ form.provinces.length }}</strong> 个省份
                </div>
              </div>

              <div v-if="form.dimension === 'heat'" class="selector-area">
                <div class="heat-options">
                  <div v-for="t in heatTypes" :key="t.value" class="heat-card"
                    :class="{ selected: form.heatType === t.value }" @click="form.heatType = t.value">
                    <el-icon :size="24" :color="form.heatType === t.value ? '#1e88e5' : '#6b7280'">
                      <component :is="t.icon" />
                    </el-icon>
                    <span>{{ t.label }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="currentStep === 3" class="step-content">
              <h3 class="section-title">选择分析指标</h3>
              <div class="metric-grid">
                <div v-for="m in availableMetrics" :key="m.value" class="metric-card"
                  :class="{ checked: form.metrics.includes(m.value) }" @click="toggleMetric(m.value)">
                  <div class="metric-check">
                    <el-icon v-if="form.metrics.includes(m.value)" :size="18" color="#fff">
                      <Check />
                    </el-icon>
                  </div>
                  <span>{{ m.label }}</span>
                </div>
              </div>
              <div v-if="form.metrics.length > 0" class="selected-info">
                已选 <strong>{{ form.metrics.length }}</strong> 个指标
              </div>
            </div>
          </div>

          <div class="panel-footer">
            <el-button v-if="currentStep > 1" @click="currentStep--" class="nav-btn">上一步</el-button>
            <el-button v-if="currentStep < 3" @click="currentStep++" :disabled="!canNext"
              class="nav-btn primary">下一步</el-button>
            <el-button v-if="currentStep === 3" @click="executeCompare" :loading="loading" class="nav-btn analyze">
              <el-icon>
                <DataAnalysis />
              </el-icon> 开始分析
            </el-button>
          </div>
        </div>

        <div v-if="result.length > 0" class="result-panel">
          <div class="result-header">
            <h3>分析结果</h3>
            <div class="view-toggle">
              <button :class="{ active: view === 'table' }" @click="view = 'table'">表格</button>
              <button :class="{ active: view === 'chart' }" @click="view = 'chart'">图表</button>
              <button :class="{ active: view === 'radar' }" @click="view = 'radar'">雷达</button>
            </div>
          </div>

          <div v-if="view === 'table'" class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="sticky-col">对比项</th>
                  <th v-for="m in form.metrics" :key="m">{{ getMetricLabel(m) }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, i) in result" :key="i">
                  <td class="sticky-col name-cell">{{ row.dimension_value }}</td>
                  <td v-for="m in form.metrics" :key="m">{{ fmt(row.data[m], m) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="view === 'chart'" ref="chartBox" class="chart-box"></div>
          <div v-if="view === 'radar'" ref="radarBox" class="chart-box"></div>

          <div class="result-actions">
            <el-button @click="saveResult" size="small">
              <el-icon>
                <Folder />
              </el-icon> 保存
            </el-button>
            <el-button @click="exportResult" size="small">
              <el-icon>
                <Download />
              </el-icon> 导出Excel
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="saveVisible" title="保存对比" width="400px" :modal="true">
      <el-form :model="saveForm">
        <el-form-item label="名称"><el-input v-model="saveForm.name" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="saveForm.desc" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveVisible = false">取消</el-button>
        <el-button type="primary" @click="doSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { School, Reading, Location, TrendCharts, Search, Check, DataAnalysis, Folder, Download } from '@element-plus/icons-vue'
import Header from '@/components/Header.vue'
import request from '@/utils/request'
import * as echarts from 'echarts'

const currentStep = ref(1)
const form = reactive({
  dimension: '',
  schoolIds: [],
  majorIds: [],
  provinces: [],
  heatType: 'comprehensive',
  metrics: [],
  timeRange: [2020, 2024]
})
const loading = ref(false)
const result = ref([])
const view = ref('table')
const chartBox = ref(null)
const radarBox = ref(null)
const saveVisible = ref(false)
const saveForm = reactive({ name: '', desc: '' })
const schoolSearch = ref('')
const majorSearch = ref('')
const provinceSearch = ref('')
const schoolOptions = ref([])
const majorOptions = ref([])
const provinceOptions = ref([])

const dimensions = [
  { value: 'school', label: '学校对比', desc: '多院校综合数据对比', icon: School, color: '#6366f1' },
  { value: 'major', label: '专业对比', desc: '各专业就业与分数对比', icon: Reading, color: '#ec4899' },
  { value: 'province', label: '地域对比', desc: '各省份教育资源对比', icon: Location, color: '#0ea5e9' },
  { value: 'heat', label: '热度排行', desc: '搜索收藏热度排行榜', icon: TrendCharts, color: '#f59e0b' }
]

const heatTypes = [
  { value: 'comprehensive', label: '综合热度', icon: TrendCharts },
  { value: 'search', label: '搜索热度', icon: Search },
  { value: 'favorite', label: '收藏热度', icon: Folder },
  { value: 'view', label: '浏览热度', icon: DataAnalysis }
]

const metricsConfig = [
  { value: 'avg_score', label: '平均分', dims: ['school', 'major', 'province'] },
  { value: 'min_score', label: '最低分', dims: ['school', 'province'] },
  { value: 'max_score', label: '最高分', dims: ['school', 'province'] },
  { value: 'avg_salary', label: '平均薪资', dims: ['major'] },
  { value: 'heat_score', label: '综合热度', dims: ['school', 'heat'] },
  { value: 'school_count', label: '学校数量', dims: ['province'] },
  { value: 'city_count', label: '城市数量', dims: ['province'] },
  { value: '985_count', label: '985院校数', dims: ['province'] },
  { value: '211_count', label: '211院校数', dims: ['province'] },
  { value: 'double_first_count', label: '双一流数', dims: ['province'] },
  { value: 'phd_count', label: '博士点数量', dims: ['school'] },
  { value: 'master_count', label: '硕士点数量', dims: ['school'] }
]

const availableMetrics = computed(() => metricsConfig.filter(m => m.dims.includes(form.dimension)))

const canNext = computed(() => {
  if (currentStep.value === 1) return !!form.dimension
  if (currentStep.value === 2) {
    if (form.dimension === 'school') return form.schoolIds.length > 0
    if (form.dimension === 'major') return form.majorIds.length > 0
    if (form.dimension === 'province') return form.provinces.length > 0
    return true
  }
  return true
})

const filteredSchools = computed(() => {
  if (!schoolSearch.value) return schoolOptions.value
  return schoolOptions.value.filter(s => s.label.includes(schoolSearch.value))
})
const filteredMajors = computed(() => {
  if (!majorSearch.value) return majorOptions.value
  return majorOptions.value.filter(m => m.label.includes(majorSearch.value))
})
const filteredProvinces = computed(() => {
  if (!provinceSearch.value) return provinceOptions.value
  return provinceOptions.value.filter(p => p.label.includes(provinceSearch.value))
})

const getDimLabel = v => { const d = dimensions.find(x => x.value === v); return d ? d.label : '' }
const getMetricLabel = v => { const m = metricsConfig.find(x => x.value === v); return m ? m.label : v }
const fmt = (v, m) => {
  if (v == null || v === undefined) return '-'
  return Number(v).toLocaleString()
}

const selectDimension = v => {
  form.dimension = v
  form.schoolIds = []
  form.majorIds = []
  form.provinces = []
  form.metrics = []
  currentStep.value = 2
}

const toggleSchool = id => {
  const i = form.schoolIds.indexOf(id)
  i > -1 ? form.schoolIds.splice(i, 1) : form.schoolIds.push(id)
}
const toggleMajor = id => {
  const i = form.majorIds.indexOf(id)
  i > -1 ? form.majorIds.splice(i, 1) : form.majorIds.push(id)
}
const toggleProvince = id => {
  const i = form.provinces.indexOf(id)
  i > -1 ? form.provinces.splice(i, 1) : form.provinces.push(id)
}
const toggleMetric = v => {
  const i = form.metrics.indexOf(v)
  i > -1 ? form.metrics.splice(i, 1) : form.metrics.push(v)
}

const executeCompare = async () => {
  if (form.metrics.length === 0) { ElMessage.warning('请至少选择一个指标'); return }
  loading.value = true
  try {
    const params = { dimension: form.dimension, metrics: form.metrics, filters: {}, time_range: form.timeRange }
    if (form.dimension === 'school') params.filters.school_ids = form.schoolIds
    else if (form.dimension === 'major') params.filters.major_ids = form.majorIds
    else if (form.dimension === 'province') params.filters.provinces = form.provinces
    else if (form.dimension === 'heat') params.filters.heat_type = form.heatType

    const res = await request.post('/analysis/compare', params)
    if (res.data.success) {
      result.value = res.data.data.data || []
      ElMessage.success('分析完成')
      nextTick(() => {
        if (view.value === 'chart') drawChart()
        else if (view.value === 'radar') drawRadar()
      })
    }
  } catch { ElMessage.error('分析失败') }
  finally { loading.value = false }
}

const drawChart = () => {
  if (!chartBox.value || !result.value.length) return
  if (chartBox.value._c) chartBox.value._c.dispose()
  const c = echarts.init(chartBox.value)
  chartBox.value._c = c
  c.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 10 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 50, containLabel: true },
    xAxis: { type: 'category', data: result.value.map(r => r.dimension_value), axisLabel: { rotate: 25 } },
    yAxis: { type: 'value' },
    series: form.metrics.map(m => ({ name: getMetricLabel(m), type: 'bar', data: result.value.map(r => r.data[m] || 0) }))
  })
  window.addEventListener('resize', () => c.resize())
}

const drawRadar = () => {
  if (!radarBox.value || !result.value.length) return
  if (radarBox.value._c) radarBox.value._c.dispose()
  const c = echarts.init(radarBox.value)
  radarBox.value._c = c
  const maxs = {}
  form.metrics.forEach(m => { maxs[m] = Math.max(...result.value.map(r => r.data[m] || 0)) * 1.2 || 100 })
  c.setOption({
    tooltip: {},
    legend: { data: result.value.map(r => r.dimension_value), left: 0, orient: 'vertical' },
    radar: { indicator: form.metrics.map(m => ({ name: getMetricLabel(m), max: maxs[m] })), radius: '65%' },
    series: [{ type: 'radar', data: result.value.map(r => ({ name: r.dimension_value, value: form.metrics.map(m => r.data[m] || 0) })) }]
  })
  window.addEventListener('resize', () => c.resize())
}

watch(view, nv => {
  if (!result.value.length) return
  nextTick(() => { if (nv === 'chart') drawChart(); else if (nv === 'radar') drawRadar() })
})

const saveResult = () => { if (!result.value.length) return; saveVisible.value = true }
const doSave = () => {
  if (!saveForm.name) { ElMessage.warning('请输入名称'); return }
  const arr = JSON.parse(localStorage.getItem('savedCompare') || '[]')
  arr.push({ id: Date.now(), name: saveForm.name, desc: saveForm.desc, data: result.value, time: new Date().toLocaleString() })
  localStorage.setItem('savedCompare', JSON.stringify(arr))
  saveVisible.value = false; saveForm.name = ''; saveForm.desc = ''
  ElMessage.success('保存成功')
}

const exportResult = async () => {
  if (!result.value.length) return
  try {
    const res = await request.post('/analysis/export', { type: 'excel', data: result.value, dimension: form.dimension, metrics: form.metrics })
    if (res.data.success) {
      const buf = Uint8Array.from(atob(res.data.data), c => c.charCodeAt(0))
      const a = document.createElement('a')
      a.href = URL.createObjectURL(new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }))
      a.download = res.data.filename || 'compare.xlsx'; a.click(); URL.revokeObjectURL(a.href)
      ElMessage.success('导出成功')
    }
  } catch { ElMessage.error('导出失败') }
}

onMounted(async () => {
  try {
    const res = await request.get('/analysis/filters')
    if (res.data.success) {
      schoolOptions.value = (res.data.data.schools || []).map(s => ({ key: s.id, label: s.name }))
      majorOptions.value = (res.data.data.majors || []).map(m => ({ key: m.id, label: m.name }))
      provinceOptions.value = (res.data.data.provinces || []).map(p => ({ key: p, label: p }))
    }
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.compare-page {
  min-height: 100vh;
  background: #f1f5f9;
  color: #1e293b;
}

.page-wrapper {
  position: relative;
}

.hero-banner {
  padding: 48px 20px 36px;
  text-align: center;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
}

.hero-content {
  position: relative;
}

.hero-title {
  font-size: 36px;
  font-weight: 700;
  color: #000000;
  margin: 0 0 8px;
}

.hero-desc {
  font-size: 15px;
  color: #64748b;
  margin: 0;
}

.main-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px 60px;
}

.config-panel {
  background: #fff;
  border-radius: 12px;
  padding: 28px;
  margin-top: 24px;
  margin-bottom: 28px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.panel-header {
  margin-bottom: 24px;
}

.step-indicators {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  background: #e2e8f0;
  color: #94a3b8;
  transition: all 0.3s;
}

.step.active .step-circle {
  background: #1e88e5;
  color: #fff;
}

.step.completed .step-circle {
  background: #10b981;
  color: #fff;
}

.step span {
  font-size: 12px;
  color: #94a3b8;
}

.step.active span {
  color: #1e88e5;
}

.step-line {
  width: 60px;
  height: 2px;
  background: #e2e8f0;
  margin: 0 12px;
}

.step-line.active {
  background: #10b981;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 18px;
  color: #1e293b;
}

.dimension-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.dim-card {
  background: #fff;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px 14px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s;
}

.dim-card:hover {
  border-color: #1e88e5;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1);
}

.dim-card.selected {
  border-color: #1e88e5;
  background: #eef2ff;
}

.dim-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}

.dim-card h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 6px;
  color: #1e293b;
}

.dim-card p {
  font-size: 12px;
  color: #64748b;
  margin: 0;
}

.search-box {
  margin-bottom: 14px;
}

.search-box :deep(.el-input__wrapper) {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.search-box :deep(.el-input__inner) {
  color: #1e293b;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 280px;
  overflow-y: auto;
  padding: 4px;
}

.tag-item {
  padding: 7px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  color: #475569;
}

.tag-item:hover {
  border-color: #1e88e5;
  color: #1e88e5;
}

.tag-item.selected {
  background: #1e88e5;
  border-color: #1e88e5;
  color: #fff;
}

.selected-info {
  margin-top: 14px;
  padding: 10px 14px;
  background: #eef2ff;
  border-radius: 6px;
  font-size: 13px;
  color: #1e88e5;
}

.selected-info strong {
  color: #1e88e5;
}

.heat-options {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.heat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.heat-card:hover {
  border-color: #1e88e5;
}

.heat-card.selected {
  border-color: #1e88e5;
  background: #eef2ff;
  color: #1e88e5;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  color: #475569;
}

.metric-card:hover {
  border-color: #1e88e5;
}

.metric-card.checked {
  border-color: #10b981;
  background: #ecfdf5;
  color: #065f46;
}

.metric-check {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 2px solid #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.metric-card.checked .metric-check {
  background: #10b981;
  border-color: #10b981;
}

.panel-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.nav-btn {
  padding: 9px 24px;
  border-radius: 8px;
  font-weight: 600;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
  color: #475569;
}

.nav-btn:hover {
  background: #f1f5f9;
}

.nav-btn.primary {
  background: #1e88e5;
  color: #fff;
  border-color: #1e88e5;
}

.nav-btn.primary:hover:not(:disabled) {
  background: #469ae3;
  border-color: #469ae3;
}

.nav-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-btn.analyze {
  background: #1e88e5;
  color: #fff;
  border-color: #1e88e5;
}

.nav-btn.analyze:hover {
  background: #469ae3;
  border-color: #469ae3;
}

.result-panel {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.result-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.view-toggle {
  display: flex;
  gap: 4px;
  background: #f1f5f9;
  padding: 3px;
  border-radius: 8px;
}

.view-toggle button {
  padding: 5px 14px;
  border: none;
  background: transparent;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.view-toggle button.active {
  background: #1e88e5;
  color: #fff;
}

.table-wrap {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th,
.data-table td {
  padding: 10px 14px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
  white-space: nowrap;
}

.data-table th {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  position: sticky;
  top: 0;
}

.data-table tbody tr:hover {
  background: #f8fafc;
}

.sticky-col {
  position: sticky;
  left: 0;
  background: #fff;
  font-weight: 600;
  color: #1e88e5;
  z-index: 1;
}

.data-table th.sticky-col {
  background: #f8fafc;
  z-index: 2;
}

.name-cell {
  color: #1e293b;
}

.chart-box {
  width: 100%;
  height: 420px;
  border-radius: 8px;
}

.result-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  justify-content: flex-end;
}

.result-actions :deep(.el-button) {
  border-radius: 6px;
}
</style>
