<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElLoading, ElTabs, ElTabPane, ElCard, ElTag, ElEmpty, ElButton, ElMessage, ElIcon } from 'element-plus'
import { Star, StarFilled } from '@element-plus/icons-vue'
import { getMajorAnalysis, getMajorSchools } from '../api/major'
import { addFavorite, removeFavorite, checkFavorite } from '../api/favorite'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const majorId = route.params.id

// 记录来源页面
const fromPage = route.query.from || 'majors'

const goBack = () => {
  if (fromPage === 'majors') {
    router.push('/majors')
  } else if (fromPage === 'home') {
    router.push('/')
  } else {
    router.back()
  }
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

// 收藏相关状态
const isLoggedIn = ref(false)
const isFavorited = ref(false)
const favoriteLoading = ref(false)

// 图表实例
let provinceChart = null

// 检查登录状态
const checkLoginStatus = () => {
  const token = localStorage.getItem('userToken')
  isLoggedIn.value = !!token
}

// 检查收藏状态
const checkFavoriteStatus = async () => {
  if (!isLoggedIn.value) return
  
  try {
    const res = await checkFavorite({
      type: 'major',
      target_id: majorId
    })
    if (res.success) {
      isFavorited.value = res.data.is_favorited
    }
  } catch (error) {
    console.error('检查收藏状态失败', error)
  }
}

// 切换收藏状态
const toggleFavorite = async () => {
  if (!isLoggedIn.value) return
  
  favoriteLoading.value = true
  try {
    if (isFavorited.value) {
      // 取消收藏
      const res = await removeFavorite({
        favorite_type: 'major',
        target_id: majorId
      })
      if (res.success) {
        isFavorited.value = false
        ElMessage.success('取消收藏成功')
      }
    } else {
      // 添加收藏
      const res = await addFavorite({
        favorite_type: 'major',
        target_id: majorId
      })
      if (res.success) {
        isFavorited.value = true
        ElMessage.success('收藏成功')
      }
    }
  } catch (error) {
    ElMessage.error('操作失败，请重试')
  } finally {
    favoriteLoading.value = false
  }
}

// 跳转到登录页面
const handleLogin = () => {
  router.push('/login')
}

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
  // 省份分布图（柱状图）
  const renderProvinceChart = () => {
    const provinceEl = document.getElementById('provinceChart')
    if (!provinceEl) {
      // 如果DOM元素不存在，延迟重试
      setTimeout(renderProvinceChart, 100)
      return
    }
    
    if (analysisData.value.province_distribution?.length) {
      // 如果已有图表实例，先销毁
      if (provinceChart) {
        provinceChart.dispose()
      }
      
      provinceChart = echarts.init(provinceEl)
      const provinces = analysisData.value.province_distribution.map(item => item.province)
      const counts = analysisData.value.province_distribution.map(item => item.count)
      provinceChart.setOption({
        title: { show: false },
        tooltip: { trigger: 'axis' },
        grid: { left: '8%', right: '5%', bottom: '15%', top: '12%', containLabel: true },
        xAxis: {
          type: 'category',
          data: provinces,
          axisLabel: { 
            rotate: 45, 
            color: '#666',
            fontSize: 12,
            margin: 15,
            interval: 0
          }
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
          barWidth: 25
        }]
      })
      
      // 监听窗口大小变化，重新渲染图表
      window.addEventListener('resize', () => {
        if (provinceChart) {
          provinceChart.resize()
        }
      })
    }
  }
  
  // 立即尝试渲染省份分布图
  renderProvinceChart()
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
    // 使用nextTick确保DOM更新完成后再渲染图表
    nextTick(() => {
      renderCharts()
    })
  }
}

const handlePageChange = (page) => {
  loadSchools(page)
}

onMounted(async () => {
  checkLoginStatus()
  await loadAnalysis()
  await checkFavoriteStatus()
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
              <el-button @click="goBack" type="primary" class="back-button">
                <i class="fas fa-arrow-left"></i> 返回
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
          
          <!-- 收藏按钮 -->
          <div class="header-actions">
            <el-button 
              v-if="isLoggedIn"
              :type="isFavorited ? 'danger' : 'primary'"
              @click="toggleFavorite"
              :loading="favoriteLoading"
            >
              <el-icon v-if="isFavorited"><StarFilled /></el-icon>
              <el-icon v-else><Star /></el-icon>
              {{ isFavorited ? '已收藏' : '收藏' }}
            </el-button>
            <el-button v-else type="primary" @click="handleLogin">
              <el-icon><Star /></el-icon> 登录后收藏
            </el-button>
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
          <!-- 专业前景 - 放在上面 -->
          <el-row :gutter="20">
            <el-col :xs="24">
              <el-card shadow="hover" class="chart-card" v-if="analysisData.employment?.prospect">
                <template #header>
                  <span><i class="fas fa-chart-line"></i> 专业前景</span>
                </template>
                <p class="prospect-text">{{ analysisData.employment.prospect }}</p>
              </el-card>
            </el-col>
          </el-row>
          
          <!-- 开设高校省份分布 - 放在下面 -->
          <el-row :gutter="20">
            <el-col :xs="24">
              <el-card shadow="hover" class="chart-card" v-if="analysisData.province_distribution?.length">
                <template #header>
                  <span><i class="fas fa-map-marked-alt"></i> 开设高校省份分布</span>
                </template>
                <div id="provinceChart" class="chart-container" style="height: 450px;"></div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 就业数据 -->
        <el-tab-pane label="就业数据" name="employment">
          <!-- 就业基本信息 -->
           <div class="employment-basic-info" v-if="analysisData.employment">
             <div class="info-item" v-if="analysisData.employment.avg_salary">
               <span class="info-label">平均薪资</span>
               <span class="info-value">{{ analysisData.employment.avg_salary }}元/月</span>
             </div>
             <div class="info-item" v-if="analysisData.employment.employment_rate">
               <span class="info-label">就业率</span>
               <span class="info-value">{{ analysisData.employment.employment_rate }}%</span>
             </div>
             <div class="info-item" v-if="analysisData.employment.satisfaction">
               <span class="info-label">满意度</span>
               <span class="info-value">{{ analysisData.employment.satisfaction }}%</span>
             </div>
           </div>

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
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 30px;
}

.back-button-wrapper {
  margin-bottom: 12px;
}

.back-button {
  font-size: 0.9rem;
  padding: 8px 16px;
  font-weight: 500;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.back-button i {
  font-size: 0.85rem;
}

.back-button:hover {
  transform: translateX(-3px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.header-left {
  flex: 1;
  min-width: 300px;
  text-align: left;
}

.header-left h1 {
  font-size: 2.4rem;
  font-weight: 700;
  margin: 0 0 12px;
  color: #1e3a8a;
  line-height: 1.2;
}

.header-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.header-meta .el-tag {
  font-size: 0.95rem;
  font-weight: 500;
  padding: 6px 12px;
}

.header-stats {
  display: flex;
  align-items: center;
  gap: 24px;
  min-width: 200px;
}

.stat-item {
  text-align: center;
  min-width: 80px;
}

.stat-item .label {
  display: block;
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 4px;
  font-weight: 500;
}

.stat-item .value {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1e88e5;
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
  text-align: justify;
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
  text-align: justify;
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

/* 就业基本信息样式 */
.employment-basic-info {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e1e8ed;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #e8e8e8;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  min-width: 80px;
}

.info-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1e88e5;
  min-width: 120px;
}

.info-desc {
  font-size: 0.9rem;
  color: #666;
  flex: 1;
}

/* 专业头部信息优化 */
.header-card {
  background: linear-gradient(135deg, #f8fafc 0%, #e8f4fd 100%);
  border: 1px solid #e1e8ed;
}

.header-left h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 10px;
}

/* 专业介绍卡片优化 */
.info-card {
  border: 1px solid #e1e8ed;
}

.info-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #f8f9fa 0%, #eef2f7 100%);
  font-size: 1.1rem;
  color: #1e88e5;
}

/* 图表卡片优化 */
.chart-card {
  border: 1px solid #e1e8ed;
}

.chart-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #f8f9fa 0%, #eef2f7 100%);
  font-size: 1.1rem;
  color: #1e88e5;
}

/* 分布卡片优化 */
.dist-card {
  border: 1px solid #e1e8ed;
}

.dist-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #f8f9fa 0%, #eef2f7 100%);
  font-size: 1rem;
  color: #1e88e5;
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