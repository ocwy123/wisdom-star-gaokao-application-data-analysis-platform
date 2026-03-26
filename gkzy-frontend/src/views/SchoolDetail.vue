<template>
  <div class="school-detail">
    <!-- 页面加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 学校详情内容 -->
    <div v-else-if="school" class="school-content">
      <!-- 返回按钮 -->
      <div class="back-button-container">
        <el-button class="back-button" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
      
      <!-- 头部信息区 -->
      <div class="school-header">
        <div class="header-background">
          <div class="header-gradient"></div>
        </div>
        <div class="header-content">
          <div class="school-basic-info">
            <div class="logo-container">
              <img 
                :src="school.logo || defaultLogo" 
                :alt="school.name" 
                class="school-logo"
                @error="handleLogoError"
              />
            </div>
            <div class="school-title-section">
              <h1 class="school-name">{{ school.name }}</h1>
              <p class="school-code">
                <span class="code-label">院校代码</span>
                <span class="code-value">{{ school.code }}</span>
              </p>
              <div class="school-tags">
                <el-tag v-if="school.is_985" type="danger" effect="dark" class="tag-985">985</el-tag>
                <el-tag v-if="school.is_211" type="warning" effect="dark" class="tag-211">211</el-tag>
                <el-tag v-if="school.is_double_first" type="success" effect="dark" class="tag-double-first">双一流</el-tag>
                <el-tag type="info" class="tag-type">{{ school.type }}</el-tag>
              </div>
            </div>
          </div>
          
          <div class="location-actions-row">
            <div class="school-location">
              <el-icon class="location-icon"><Position /></el-icon>
              <span>{{ school.province }} {{ school.city }}</span>
            </div>
            
            <!-- 收藏按钮 -->
            <div class="header-actions">
              <el-button 
                v-if="isLoggedIn"
                :type="isFavorited ? 'danger' : 'primary'"
                @click="toggleFavorite"
                :loading="favoriteLoading"
                class="favorite-btn"
              >
                <el-icon v-if="isFavorited"><StarFilled /></el-icon>
                <el-icon v-else><Star /></el-icon>
                {{ isFavorited ? '已收藏' : '收藏' }}
              </el-button>
              <el-button v-else type="primary" @click="handleLogin" class="favorite-btn">
                <el-icon><Star /></el-icon> 登录后收藏
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 统计信息卡片 -->
      <div class="stats-section">
        <div class="stat-card">
          <el-icon class="stat-icon"><Timer /></el-icon>
          <div class="stat-content">
            <p class="stat-value">{{ school.founded_year || '未知' }}</p>
            <p class="stat-label">建校时间</p>
          </div>
        </div>
        <div class="stat-card">
          <el-icon class="stat-icon"><Star /></el-icon>
          <div class="stat-content">
            <p class="stat-value">{{ school.phd_count || 0 }}</p>
            <p class="stat-label">博士点</p>
          </div>
        </div>
        <div class="stat-card">
          <el-icon class="stat-icon"><Medal /></el-icon>
          <div class="stat-content">
            <p class="stat-value">{{ school.master_count || 0 }}</p>
            <p class="stat-label">硕士点</p>
          </div>
        </div>
        <div class="stat-card">
          <el-icon class="stat-icon"><Link /></el-icon>
          <div class="stat-content">
            <p v-if="school.website" class="stat-value website-value">
              <a 
                :href="school.website" 
                target="_blank" 
                rel="noopener noreferrer"
                class="website-link"
              >
                访问官网
              </a>
            </p>
            <p v-else class="stat-value">未提供</p>
            <p class="stat-label">官方网站</p>
          </div>
        </div>
      </div>

      <!-- 详细介绍区 -->
      <div class="school-description-section">
        <div class="section-header">
          <el-icon class="section-icon"><Document /></el-icon>
          <h2 class="section-title">学校简介</h2>
        </div>
        <div class="description-content">
          <p v-for="(paragraph, index) in descriptionParagraphs" :key="index" class="description-paragraph">
            {{ paragraph }}
          </p>
        </div>
      </div>

      <!-- 特色标签区 -->
      <div class="features-section">
        <div class="section-header">
          <el-icon class="section-icon"><CollectionTag /></el-icon>
          <h2 class="section-title">学校特色</h2>
        </div>
        <div class="features-grid">
          <div v-if="school.is_985" class="feature-item">
            <el-icon class="feature-icon"><Top /></el-icon>
            <span class="feature-text">985工程重点建设高校</span>
          </div>
          <div v-if="school.is_211" class="feature-item">
            <el-icon class="feature-icon"><Trophy /></el-icon>
            <span class="feature-text">211工程重点建设高校</span>
          </div>
          <div v-if="school.is_double_first" class="feature-item">
            <el-icon class="feature-icon"><Flag /></el-icon>
            <span class="feature-text">双一流建设高校</span>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Location /></el-icon>
            <span class="feature-text">{{ school.province }}省{{ school.city }}市</span>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Briefcase /></el-icon>
            <span class="feature-text">{{ school.type }}</span>
          </div>
        </div>
      </div>

      <!-- 分数线趋势图区 -->
      <div class="score-trend-section">
        <div class="section-header">
          <el-icon class="section-icon"><DataAnalysis /></el-icon>
          <h2 class="section-title">历年分数线趋势</h2>
        </div>
        
        <!-- 筛选条件 -->
        <div class="filter-section">
          <el-form :inline="true" class="filter-form">
            <el-form-item label="省份">
              <el-select 
                v-model="selectedProvince" 
                placeholder="请选择省份"
                @change="handleProvinceChange"
                class="filter-select"
              >
                <el-option 
                  v-for="province in provinces" 
                  :key="province" 
                  :label="province" 
                  :value="province"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="专业">
              <el-select 
                v-model="selectedMajor" 
                placeholder="请选择专业"
                @change="handleMajorChange"
                class="filter-select"
                :disabled="!selectedProvince"
              >
                <el-option 
                  v-for="major in majors" 
                  :key="major" 
                  :label="major" 
                  :value="major"
                />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 图表区域 -->
        <div v-if="scoreData.length > 0" class="chart-container">
          <div ref="chartRef" class="score-chart"></div>
        </div>
        <div v-else-if="selectedProvince && selectedMajor" class="no-data-container">
          <el-icon class="no-data-icon"><DocumentRemove /></el-icon>
          <p>暂无该专业的分数线数据</p>
        </div>
        <div v-else class="select-tip-container">
          <el-icon class="select-tip-icon"><InfoFilled /></el-icon>
          <p>请选择省份和专业查看分数线趋势</p>
        </div>
      </div>

      <!-- 装饰元素 -->
      <div class="decorative-elements">
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-container">
      <el-icon class="error-icon"><Warning /></el-icon>
      <p>加载学校信息失败，请稍后重试</p>
      <el-button type="primary" @click="fetchSchoolDetail">重新加载</el-button>
      <el-button type="info" @click="testApi">测试API</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSchoolDetail, getSchoolProvinces, getSchoolMajors, getAdmissionScores } from '../api/school'
import { addFavorite, removeFavorite, checkFavorite } from '../api/favorite'
import { Position, ArrowRight, ArrowLeft, Warning, Loading, Timer, Star, Medal, Link, Document, CollectionTag, Top, Trophy, Flag, Location, Briefcase, DataAnalysis, DocumentRemove, InfoFilled, StarFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const school = ref(null)
const defaultLogo = 'https://via.placeholder.com/120x120?text=Logo'

// 收藏相关状态
const isLoggedIn = ref(false)
const isFavorited = ref(false)
const favoriteLoading = ref(false)

// 分数线相关变量
const provinces = ref([])
const majors = ref([])
const scoreData = ref([])
const selectedProvince = ref('')
const selectedMajor = ref('')
const chartRef = ref(null)
let chartInstance = null

// 从URL参数获取学校ID，默认使用298（西安交通大学）
const schoolId = computed(() => {
  console.log('Route params:', route.params)
  const id = route.params.id || 298
  console.log('School ID:', id)
  return id
})

// 将学校简介按换行符分割成段落
const descriptionParagraphs = computed(() => {
  if (!school.value || !school.value.description) return ['暂无简介']
  return school.value.description.split('\n').filter(p => p.trim())
})

// 处理校徽图片加载失败
const handleLogoError = (event) => {
  event.target.src = defaultLogo
}

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
      type: 'school',
      target_id: route.params.id
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
        favorite_type: 'school',
        target_id: route.params.id
      })
      if (res.success) {
        isFavorited.value = false
        ElMessage.success('取消收藏成功')
      }
    } else {
      // 添加收藏
      const res = await addFavorite({
        favorite_type: 'school',
        target_id: route.params.id
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

const goBack = () => {
  router.back()
}

// 获取学校详情
const fetchSchoolDetail = async () => {
  loading.value = true
  try {
    console.log('=== Fetching school detail ===')
    console.log('School ID:', schoolId.value)
    
    // 直接使用fetch API测试
    const response = await fetch(`http://localhost:5000/api/school/detail/${schoolId.value}`)
    console.log('Fetch response:', response)
    
    if (response.ok) {
      const data = await response.json()
      console.log('Parsed data:', data)
      
      if (data.code === 200 && data.data) {
        school.value = data.data
        console.log('School value set:', school.value)
        // 获取学校招生省份列表
        await fetchProvinces()
      } else {
        console.log('Invalid response data:', data)
      }
    } else {
      console.log('Response not ok:', response.status)
    }
  } catch (error) {
    console.error('=== Error fetching school detail ===')
    console.error('Error message:', error.message)
    console.error('Error stack:', error.stack)
  } finally {
    loading.value = false
    console.log('=== Fetch school detail completed ===')
    console.log('School value:', school.value)
    console.log('Loading value:', loading.value)
  }
}

// 获取学校招生省份列表
const fetchProvinces = async () => {
  try {
    console.log('=== Fetching provinces ===')
    // 直接使用fetch API测试
    const response = await fetch(`http://localhost:5000/api/school/${schoolId.value}/provinces`)
    console.log('Provinces fetch response:', response)
    
    if (response.ok) {
      const data = await response.json()
      console.log('Provinces parsed data:', data)
      
      if (data.code === 200 && data.data) {
        provinces.value = data.data
        console.log('Provinces value set:', provinces.value)
      } else {
        console.log('Invalid provinces response data:', data)
      }
    } else {
      console.log('Provinces response not ok:', response.status)
    }
  } catch (error) {
    console.error('Failed to fetch provinces:', error)
  }
}

// 获取学校在指定省份的专业列表
const fetchMajors = async (province) => {
  try {
    console.log('=== Fetching majors ===')
    // 直接使用fetch API测试
    const response = await fetch(`http://localhost:5000/api/school/${schoolId.value}/majors?province=${encodeURIComponent(province)}`)
    console.log('Majors fetch response:', response)
    
    if (response.ok) {
      const data = await response.json()
      console.log('Majors parsed data:', data)
      
      if (data.code === 200 && data.data) {
        majors.value = data.data
        console.log('Majors value set:', majors.value)
      } else {
        console.log('Invalid majors response data:', data)
      }
    } else {
      console.log('Majors response not ok:', response.status)
    }
  } catch (error) {
    console.error('Failed to fetch majors:', error)
  }
}

// 获取学校专业分数线数据
const fetchScores = async (province, major) => {
  try {
    console.log('=== Fetching scores ===')
    // 直接使用fetch API测试
    const response = await fetch(`http://localhost:5000/api/school/${schoolId.value}/scores?province=${encodeURIComponent(province)}&major=${encodeURIComponent(major)}`)
    console.log('Scores fetch response:', response)
    
    if (response.ok) {
      const data = await response.json()
      console.log('Scores parsed data:', data)
      
      if (data.code === 200 && data.data) {
        scoreData.value = data.data
        console.log('Score data set:', scoreData.value)
        // 等待DOM更新后再渲染图表
        nextTick(() => {
          console.log('After nextTick - Chart ref:', chartRef.value)
          renderChart()
        })
      } else {
        console.log('Invalid scores response data:', data)
      }
    } else {
      console.log('Scores response not ok:', response.status)
    }
  } catch (error) {
    console.error('Failed to fetch scores:', error)
  }
}

// 处理省份选择变化
const handleProvinceChange = (province) => {
  selectedMajor.value = ''
  scoreData.value = []
  if (province) {
    fetchMajors(province)
  }
}

// 处理专业选择变化
const handleMajorChange = (major) => {
  scoreData.value = []
  if (selectedProvince.value && major) {
    fetchScores(selectedProvince.value, major)
  }
}

// 渲染分数线趋势图
const renderChart = () => {
  console.log('=== Rendering chart ===')
  console.log('Chart ref:', chartRef.value)
  console.log('Score data length:', scoreData.value.length)
  
  if (!chartRef.value) {
    console.log('Chart ref is null')
    return
  }
  
  if (scoreData.value.length === 0) {
    console.log('Score data is empty')
    return
  }
  
  try {
    // 销毁旧图表
    if (chartInstance) {
      console.log('Disposing old chart instance')
      chartInstance.dispose()
    }
    
    // 创建新图表
    console.log('Creating new chart instance')
    chartInstance = echarts.init(chartRef.value)
    
    // 准备数据
    console.log('Preparing chart data')
    const years = scoreData.value.map(item => item.year)
    const scores = scoreData.value.map(item => item.min_score)
    
    console.log('Years:', years)
    console.log('Scores:', scores)
    
    // 检查数据有效性
    if (scores.some(isNaN)) {
      console.log('Invalid data detected')
      return
    }
    
    // 计算线性回归并预测到2026年的分数
    let predictedYears = []
    let predictedScores = []
    
    if (years.length >= 2) {
      // 计算线性回归参数
      const n = years.length
      const sumX = years.reduce((a, b) => a + b, 0)
      const sumY = scores.reduce((a, b) => a + b, 0)
      const sumXY = years.reduce((sum, x, i) => sum + x * scores[i], 0)
      const sumX2 = years.reduce((sum, x) => sum + x * x, 0)
      
      const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
      const intercept = (sumY - slope * sumX) / n
      
      // 预测到2026年的分数
      const maxYear = Math.max(...years)
      for (let year = maxYear + 1; year <= 2026; year++) {
        predictedYears.push(year)
        predictedScores.push(slope * year + intercept)
      }
      
      console.log('Linear regression - Slope:', slope)
      console.log('Linear regression - Intercept:', intercept)
      console.log('Predicted years:', predictedYears)
      console.log('Predicted scores:', predictedScores)
    }
    
    // 计算图表配置参数
    const allScores = [...scores, ...predictedScores]
    const minScore = Math.min(...allScores)
    const maxScore = Math.max(...allScores)
    
    console.log('Min score:', minScore)
    console.log('Max score:', maxScore)
    
    // 图表配置
    const option = {
      title: {
        text: `${school.value.name} ${selectedMajor.value}专业分数线趋势`,
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          crossStyle: {
            color: '#999'
          }
        }
      },
      legend: {
        data: ['最低分', '预测分数'],
        top: 30
      },
      xAxis: [
        {
          type: 'category',
          data: [...years, ...predictedYears],
          axisPointer: {
            type: 'shadow'
          }
        }
      ],
      yAxis: [
        {
          type: 'value',
          name: '最低分',
          min: Math.floor(minScore * 0.95),
          max: Math.ceil(maxScore * 1.05),
          interval: 10,
          axisLabel: {
            formatter: '{value}'
          }
        }
      ],
      series: [
        {
          name: '最低分',
          type: 'line',
          data: scores,
          smooth: false,
          itemStyle: {
            color: '#aa3bff'
          },
          lineStyle: {
            width: 3
          },
          symbol: 'circle',
          symbolSize: 8
        },
        {
          name: '预测分数',
          type: 'line',
          data: [...Array(scores.length - 1).fill(null), scores[scores.length - 1], ...predictedScores],
          smooth: true,
          itemStyle: {
            color: '#ff7875'
          },
          lineStyle: {
            width: 3,
            type: 'dashed'
          },
          symbol: 'diamond',
          symbolSize: 10
        }
      ]
    }
    
    // 应用配置
    console.log('Setting chart option')
    chartInstance.setOption(option)
    console.log('Chart rendered successfully')
    
    // 监听窗口大小变化
    window.addEventListener('resize', handleResize)
  } catch (error) {
    console.error('Error rendering chart:', error)
  }
}

// 处理窗口大小变化
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 组件挂载时获取学校详情
onMounted(async () => {
  checkLoginStatus()
  await fetchSchoolDetail()
  await checkFavoriteStatus()
})

// 测试API调用
const testApi = async () => {
  try {
    console.log('=== Testing API ===')
    const response = await fetch('http://localhost:5000/api/school/detail/298')
    console.log('Fetch response:', response)
    const data = await response.json()
    console.log('Parsed data:', data)
  } catch (error) {
    console.error('Error testing API:', error)
  }
}

// 组件卸载时清理
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.school-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  min-height: 100vh;
  background: #fafbfc;
  color: #333;
  position: relative;
  overflow: hidden;
}

/* ===== 返回按钮 ===== */
.back-button-container {
  margin-bottom: 20px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border: none;
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  color: white;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(30, 136, 229, 0.2);
}

.back-button:hover {
  transform: translateX(-4px);
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
}

.back-button .el-icon {
  font-size: 16px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 16px;
  z-index: 10;
  position: relative;
}

.loading-icon {
  font-size: 48px;
  color: #1e88e5;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 16px;
  text-align: center;
  z-index: 10;
  position: relative;
}

.error-icon {
  font-size: 48px;
  color: #f56c6c;
}

.school-content {
  animation: fadeIn 0.5s ease-out;
  position: relative;
  z-index: 5;
}

/* 头部信息区 */
.school-header {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
  background: white;
}

.school-header:hover {
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.header-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  z-index: 1;
}

.header-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0) 100%);
}

.header-content {
  position: relative;
  z-index: 2;
  padding: 48px 32px 32px;
  margin-top: 80px;
}

.school-basic-info {
  display: flex;
  align-items: center;
  gap: 32px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.logo-container {
  flex-shrink: 0;
  width: 140px;
  height: 140px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: -70px;
  border: 4px solid white;
  transition: all 0.3s ease;
}

.logo-container:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 32px rgba(0,0,0,0.3);
}

.school-logo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.logo-container:hover .school-logo {
  transform: scale(1.1);
}

.school-title-section {
  flex: 1;
  min-width: 300px;
}

.school-name {
  font-size: 36px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 12px 0;
  letter-spacing: 1px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.school-code {
  font-size: 16px;
  color: #333;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

.school-code .code-label {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  letter-spacing: 1px;
}

.school-code .code-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e88e5;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  padding: 8px 20px;
  border-radius: 8px;
  border: 2px solid #90caf9;
  font-family: 'Courier New', monospace;
  letter-spacing: 1px;
  box-shadow: 0 2px 8px rgba(30, 136, 229, 0.15);
  transition: all 0.3s ease;
}

.school-code .code-value:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.25);
  border-color: #1e88e5;
}

.location-actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-top: 24px;
  flex-wrap: wrap;
}

.school-location {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  color: #1e88e5;
  background: #e3f2fd;
  padding: 12px 20px;
  border-radius: 25px;
  transition: all 0.3s ease;
  border: 2px solid #bbdefb;
  font-weight: 500;
}

.school-location:hover {
  background: #1e88e5;
  color: white;
  transform: translateX(8px);
  border-color: #1565c0;
}

.location-icon {
  color: #1e88e5;
  font-size: 18px;
  transition: all 0.3s ease;
}

.school-location:hover .location-icon {
  color: white;
}

.school-tags {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.tag-985, .tag-211, .tag-double-first, .tag-type {
  font-weight: 600;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.tag-985:hover, .tag-211:hover, .tag-double-first:hover, .tag-type:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* 收藏按钮样式 */
.header-actions {
  flex-shrink: 0;
}

.favorite-btn {
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 25px;
  border: none;
  box-shadow: 0 4px 15px rgba(30, 136, 229, 0.2);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.favorite-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(30, 136, 229, 0.3);
}

.favorite-btn:active {
  transform: translateY(-1px);
}

/* 统计信息卡片 */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 15px 30px rgba(0,0,0,0.1);
}

.stat-card:hover::before {
  width: 8px;
}

.stat-icon {
  font-size: 32px;
  color: #1e88e5;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.stat-card:hover .stat-icon {
  transform: scale(1.2);
  rotate: 15deg;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 4px 0;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.website-value {
  font-size: 18px;
}

.website-link {
  color: #1e88e5;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.website-link:hover {
  color: #1565c0;
  text-decoration: underline;
  transform: translateX(4px);
}

/* 详细介绍区 */
.school-description-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  margin-bottom: 32px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.school-description-section:hover {
  box-shadow: 0 15px 30px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e3f2fd;
}

.section-icon {
  font-size: 24px;
  color: #1e88e5;
  flex-shrink: 0;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.description-content {
  line-height: 1.8;
  font-size: 16px;
  color: #333;
  position: relative;
  z-index: 1;
}

.description-paragraph {
  margin: 0 0 20px 0;
  text-align: justify;
  position: relative;
  padding-left: 20px;
}

.description-paragraph::before {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #1e88e5;
}

.description-paragraph:last-child {
  margin-bottom: 0;
}

/* 特色标签区 */
.features-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
  margin-bottom: 32px;
}

.features-section:hover {
  box-shadow: 0 15px 30px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #e3f2fd;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.feature-item:hover {
  background: white;
  border-color: #1e88e5;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(30, 136, 229, 0.15);
}

.feature-icon {
  font-size: 20px;
  color: #1e88e5;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.feature-item:hover .feature-icon {
  transform: scale(1.2);
  rotate: 15deg;
}

.feature-text {
  font-size: 14px;
  color: #1a1a1a;
  font-weight: 500;
  flex: 1;
}

/* 分数线趋势图区 */
.score-trend-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
  margin-bottom: 32px;
  position: relative;
  overflow: hidden;
}

.score-trend-section:hover {
  box-shadow: 0 15px 30px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

/* 筛选条件 */
.filter-section {
  margin-bottom: 32px;
  padding: 24px;
  background: #e3f2fd;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.filter-section:hover {
  background: #bbdefb;
}

.filter-form {
  display: flex;
  gap: 24px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  width: 200px;
}

/* 图表容器 */
.chart-container {
  position: relative;
  height: 400px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  background: #f9f9f9;
  padding: 24px;
}

.score-chart {
  width: 100%;
  height: 100%;
}

/* 无数据状态 */
.no-data-container,
.select-tip-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 16px;
  text-align: center;
  background: #f9f9f9;
  border-radius: 12px;
  border: 2px dashed #e0e0e0;
}

.no-data-icon,
.select-tip-icon {
  font-size: 48px;
  color: #999;
  opacity: 0.5;
}

.no-data-container p,
.select-tip-container p {
  font-size: 16px;
  color: #666;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .score-trend-section {
    padding: 24px;
  }
  
  .filter-form {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .chart-container {
    height: 300px;
    padding: 16px;
  }
  
  .no-data-container,
  .select-tip-container {
    height: 200px;
  }
}

/* 装饰元素 */
.decorative-elements {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

@keyframes float {
  0% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
  100% {
    transform: translateY(0px) rotate(360deg);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .school-detail {
    padding: 16px;
  }
  
  .header-content {
    padding: 40px 24px 24px;
  }
  
  .school-basic-info {
    flex-direction: column;
    text-align: center;
    gap: 24px;
  }
  
  .logo-container {
    margin-top: -60px;
    width: 120px;
    height: 120px;
  }
  
  .school-name {
    font-size: 28px;
  }
  
  .school-location {
    margin: 20px auto 0;
  }
  
  .stats-section {
    grid-template-columns: 1fr;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .school-description-section,
  .features-section {
    padding: 24px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .decorative-circle {
    display: none;
  }
}

@media (max-width: 480px) {
  .school-name {
    font-size: 24px;
  }
  
  .header-background {
    height: 150px;
  }
  
  .header-content {
    padding: 32px 20px 20px;
  }
  
  .logo-container {
    width: 100px;
    height: 100px;
    margin-top: -50px;
  }
  
  .school-tags {
    justify-content: center;
  }
}
</style>