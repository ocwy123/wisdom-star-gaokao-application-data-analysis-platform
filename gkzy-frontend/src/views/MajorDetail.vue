<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElLoading, ElTabs, ElTabPane, ElCard, ElTag, ElEmpty, ElButton } from 'element-plus'
import { getMajorAnalysis, getMajorSchools } from '../api/major'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const majorId = route.params.id

const goBack = () => {
  router.push('/majors')
}

const analysisData = ref(null)
const schools = ref([])
const schoolsPagination = ref({
  page: 1,
  size: 10,
  total: 0
})
const loading = ref(true)
const activeTab = ref('overview')

// 图表实例
let salaryChart = null
let provinceChart = null

// 加载分析数据
const loadAnalysis = async () => {
  const loadingInstance = ElLoading.service({ fullscreen: true, text: '加载专业信息...' })
  loading.value = true
  try {
    const res = await getMajorAnalysis(majorId)
    analysisData.value = res.data
    await nextTick()
    renderCharts()
  } catch (error) {
    console.error('加载专业分析失败', error)
  } finally {
    loading.value = false
    loadingInstance.close()
  }
}

// 渲染图表
const renderCharts = () => {
  // 薪资趋势图
  const salaryEl = document.getElementById('salaryChart')
  if (salaryEl && analysisData.value.salary_trend?.length) {
    salaryChart = echarts.init(salaryEl)
    salaryChart.setOption({
      title: { show: false },
      tooltip: { trigger: 'axis' },
      grid: { left: '5%', right: '5%', bottom: '5%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: analysisData.value.salary_trend.map(item => item.year + '年'),
        axisLabel: { color: '#666' }
      },
      yAxis: {
        type: 'value',
        name: '元/月',
        nameTextStyle: { color: '#999' },
        axisLabel: { color: '#666' }
      },
      series: [{
        data: analysisData.value.salary_trend.map(item => item.avg_salary),
        type: 'line',
        smooth: true,
        lineStyle: { color: '#667eea', width: 3 },
        areaStyle: { color: 'rgba(102,126,234,0.1)' },
        symbol: 'circle',
        symbolSize: 8
      }]
    })
  }

  // 省份分布图（柱状图）
  const provinceEl = document.getElementById('provinceChart')
  if (provinceEl && analysisData.value.province_distribution?.length) {
    provinceChart = echarts.init(provinceEl)
    const provinces = analysisData.value.province_distribution.map(item => item.province)
    const counts = analysisData.value.province_distribution.map(item => item.count)
    provinceChart.setOption({
      title: { show: false },
      tooltip: { trigger: 'axis' },
      grid: { left: '5%', right: '5%', bottom: '10%', top: '5%', containLabel: true },
      xAxis: {
        type: 'category',
        data: provinces,
        axisLabel: { rotate: 30, color: '#666' }
      },
      yAxis: {
        type: 'value',
        name: '开设高校数',
        nameTextStyle: { color: '#999' },
        axisLabel: { color: '#666' }
      },
      series: [{
        data: counts,
        type: 'bar',
        itemStyle: { color: '#667eea', borderRadius: [4,4,0,0] },
        barWidth: 20
      }]
    })
  }
}

// 加载开设高校
const loadSchools = async (page = 1) => {
  const loadingInstance = ElLoading.service({ target: '.school-list', text: '加载高校列表...' })
  try {
    const params = { page, size: schoolsPagination.value.size }
    const res = await getMajorSchools(majorId, params)
    schools.value = res.data.list
    schoolsPagination.value.total = res.data.total
    schoolsPagination.value.page = page
  } catch (error) {
    console.error('加载高校列表失败', error)
  } finally {
    loadingInstance.close()
  }
}

const handleTabChange = (tab) => {
  activeTab.value = tab.paneName || tab
  if (activeTab.value === 'schools' && schools.value.length === 0) {
    loadSchools()
  }
  if (activeTab.value === 'overview') {
    setTimeout(renderCharts, 100)
  }
}

const handlePageChange = (page) => {
  loadSchools(page)
}

onMounted(() => {
  loadAnalysis()
})
</script>

<template>
  <div class="major-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="analysisData" class="detail-content">
      <!-- 专业头部信息 -->
      <el-card class="header-card" :body-style="{ padding: '30px' }">
        <div class="major-header">
          <div class="header-left">
            <div class="back-button-wrapper">
              <el-button @click="goBack" type="primary" link class="back-button">
                <i class="fas fa-arrow-left"></i> 返回专业列表
              </el-button>
            </div>
            <h1>{{ analysisData.major_info.name }}</h1>
            <div class="header-meta">
              <el-tag size="large" type="info" effect="plain">{{ analysisData.major_info.code }}</el-tag>
              <el-tag size="large" type="success" effect="light">{{ analysisData.school_count }} 所高校开设</el-tag>
            </div>
          </div>
          <div class="header-stats">
            <div class="stat-item">
              <span class="label">学制</span>
              <span class="value">{{ analysisData.major_info.duration }}年</span>
            </div>
            <el-divider direction="vertical" />
            <div class="stat-item">
              <span class="label">学位</span>
              <span class="value">{{ analysisData.major_info.degree || '暂无' }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 专业介绍卡片 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <span><i class="fas fa-info-circle"></i> 专业介绍</span>
        </template>
        <p>{{ analysisData.major_info.description }}</p>
        <el-tag v-if="analysisData.major_info.subjects" type="primary" effect="light" class="subjects-tag">
          <i class="fas fa-flask"></i> 选科建议：{{ analysisData.major_info.subjects }}
        </el-tag>
      </el-card>

      <!-- Tabs 切换 -->
      <el-tabs v-model="activeTab" @tab-click="handleTabChange" class="detail-tabs">
        <!-- 专业概况 -->
        <el-tab-pane label="专业概况" name="overview">
          <el-row :gutter="20">
            <el-col :xs="24" :lg="12">
              <el-card shadow="hover" class="chart-card" v-if="analysisData.province_distribution?.length">
                <template #header>
                  <span><i class="fas fa-map-marked-alt"></i> 开设高校省份分布</span>
                </template>
                <div id="provinceChart" class="chart-container"></div>
              </el-card>
            </el-col>
            <el-col :xs="24" :lg="12">
              <el-card shadow="hover" class="chart-card" v-if="analysisData.employment?.prospect">
                <template #header>
                  <span><i class="fas fa-chart-line"></i> 专业前景</span>
                </template>
                <p class="prospect-text">{{ analysisData.employment.prospect }}</p>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 就业数据 -->
        <el-tab-pane label="就业数据" name="employment">
          <el-row :gutter="20">
            <el-col :span="24">
              <el-card shadow="hover" class="chart-card" v-if="analysisData.salary_trend?.length">
                <template #header>
                  <span><i class="fas fa-chart-bar"></i> 平均薪资趋势 (元/月)</span>
                </template>
                <div id="salaryChart" class="chart-container" style="height: 350px;"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" class="employment-detail" v-if="analysisData.employment">
            <!-- 行业分布 -->
            <el-col :xs="24" :md="8" v-if="analysisData.employment.industry_distribution">
              <el-card shadow="hover" class="dist-card">
                <template #header>
                  <span><i class="fas fa-industry"></i> 行业分布</span>
                </template>
                <div class="distribution-list">
                  <div v-for="(value, key) in JSON.parse(analysisData.employment.industry_distribution)" 
                       :key="key" class="dist-item">
                    <span class="dist-key">{{ key }}</span>
                    <el-progress :percentage="value" :format="() => value + '%'" />
                  </div>
                </div>
              </el-card>
            </el-col>
            <!-- 地区分布 -->
            <el-col :xs="24" :md="8" v-if="analysisData.employment.region_distribution">
              <el-card shadow="hover" class="dist-card">
                <template #header>
                  <span><i class="fas fa-globe-asia"></i> 地区分布</span>
                </template>
                <div class="distribution-list">
                  <div v-for="(value, key) in JSON.parse(analysisData.employment.region_distribution)" 
                       :key="key" class="dist-item">
                    <span class="dist-key">{{ key }}</span>
                    <el-progress :percentage="value" :format="() => value + '%'" />
                  </div>
                </div>
              </el-card>
            </el-col>
            <!-- 岗位分布 -->
            <el-col :xs="24" :md="8" v-if="analysisData.employment.post_distribution">
              <el-card shadow="hover" class="dist-card">
                <template #header>
                  <span><i class="fas fa-user-tie"></i> 岗位分布</span>
                </template>
                <div class="distribution-list">
                  <div v-for="(value, key) in JSON.parse(analysisData.employment.post_distribution)" 
                       :key="key" class="dist-item">
                    <span class="dist-key">{{ key }}</span>
                    <el-progress :percentage="value" :format="() => value + '%'" />
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 无就业数据 -->
          <el-empty v-else description="暂无就业数据" />
        </el-tab-pane>

        <!-- 开设高校 -->
        <el-tab-pane label="开设高校" name="schools">
          <el-card shadow="never" :body-style="{ padding: '20px 0' }">
            <div class="school-list-header">
              <span>共 {{ schoolsPagination.total }} 所高校开设此专业</span>
            </div>
            <el-row :gutter="20" class="school-list">
              <el-col
                v-for="school in schools"
                :key="school.school_id"
                :xs="24"
                :md="12"
              >
                <el-card shadow="hover" class="school-card">
                  <div class="school-card-header">
                    <h5>{{ school.school_name }}</h5>
                    <div class="school-tags">
                      <el-tag v-if="school.is_985" size="small" type="danger" effect="dark">985</el-tag>
                      <el-tag v-if="school.is_211" size="small" type="warning" effect="dark">211</el-tag>
                      <el-tag v-if="school.is_double_first" size="small" type="success" effect="dark">双一流</el-tag>
                    </div>
                  </div>
                  <div class="school-info">
                    <span><i class="fas fa-map-pin"></i> {{ school.province }} {{ school.city }}</span>
                    <span><i class="fas fa-tag"></i> {{ school.type }}</span>
                  </div>
                  <p class="school-desc">{{ school.description || '暂无详细介绍' }}</p>
                </el-card>
              </el-col>
            </el-row>

            <!-- 分页 -->
            <div class="pagination-wrapper" v-if="schoolsPagination.total > schoolsPagination.size">
              <el-pagination
                background
                layout="prev, pager, next"
                :total="schoolsPagination.total"
                :page-size="schoolsPagination.size"
                :current-page="schoolsPagination.page"
                @current-change="handlePageChange"
              />
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<style scoped>
.major-detail-container {
  max-width: 1800px;      /* 增加最大宽度 */
  margin: 0;
  padding: 20px; /* 减小左右内边距 */
}

.loading-state {
  padding: 50px;
}

.header-card {
  margin-bottom: 25px;
  border-radius: 20px;
  overflow: hidden;
}

.major-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.back-button-wrapper {
  margin-bottom: 15px;
}

.back-button {
  font-size: 0.95rem;
  color: #667eea;
  padding: 0;
}

.back-button:hover {
  color: #5a6fd8;
}

.header-left h1 {
  font-size: 2.2rem;
  margin: 0 0 10px;
  color: #333;
}

.header-meta {
  display: flex;
  gap: 15px;
  align-items: center;
}

.header-stats {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-item .label {
  display: block;
  font-size: 0.9rem;
  color: #999;
  margin-bottom: 5px;
}

.stat-item .value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #667eea;
}

.info-card {
  margin-bottom: 25px;
  border-radius: 16px;
}

.info-card :deep(.el-card__header) {
  background: #f8f9fa;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}

.info-card p {
  line-height: 1.8;
  color: #555;
  margin-bottom: 15px;
}

.subjects-tag {
  margin-top: 10px;
}

.detail-tabs {
  margin-top: 20px;
}

.chart-card {
  margin-bottom: 20px;
  border-radius: 16px;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.prospect-text {
  line-height: 1.8;
  color: #555;
  font-size: 1rem;
  min-height: 100px;
}

.employment-detail {
  margin-top: 20px;
}

.dist-card {
  margin-bottom: 20px;
  border-radius: 16px;
  height: 100%;
}

.dist-card :deep(.el-card__header) {
  background: #f8f9fa;
  font-weight: 600;
}

.distribution-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.dist-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.dist-key {
  font-size: 0.95rem;
  color: #333;
}

.school-list-header {
  padding: 0 0 20px;
  font-size: 1.1rem;
  color: #666;
  border-bottom: 1px solid #eee;
}

.school-list {
  margin-top: 20px;
}

.school-card {
  margin-bottom: 20px;
  border-radius: 16px;
  transition: transform 0.3s;
}

.school-card:hover {
  transform: translateY(-3px);
}

.school-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.school-card-header h5 {
  font-size: 1.1rem;
  margin: 0;
  color: #333;
}

.school-tags {
  display: flex;
  gap: 5px;
}

.school-info {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
  font-size: 0.9rem;
  color: #666;
}

.school-info span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.school-desc {
  color: #555;
  line-height: 1.6;
  font-size: 0.9rem;
  margin: 0;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

/* 响应式 */
@media (max-width: 768px) {
  .major-detail-container {
    padding: 20px 15px;
  }
  .major-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-stats {
    width: 100%;
    justify-content: space-around;
  }
}
</style>