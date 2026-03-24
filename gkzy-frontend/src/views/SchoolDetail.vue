<template>
  <div class="school-detail">
    <!-- 页面加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 学校详情内容 -->
    <div v-else-if="school" class="school-content">
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
              <p class="school-code">{{ school.code }}</p>
              <div class="school-tags">
                <el-tag v-if="school.is_985" type="danger" effect="dark" class="tag-985">985</el-tag>
                <el-tag v-if="school.is_211" type="warning" effect="dark" class="tag-211">211</el-tag>
                <el-tag v-if="school.is_double_first" type="success" effect="dark" class="tag-double-first">双一流</el-tag>
                <el-tag type="info" class="tag-type">{{ school.type }}</el-tag>
              </div>
            </div>
          </div>
          <div class="school-location">
            <el-icon class="location-icon"><Position /></el-icon>
            <span>{{ school.province }} {{ school.city }}</span>
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

      <!-- 装饰元素 -->
      <div class="decorative-elements">
        <div class="decorative-circle circle-1"></div>
        <div class="decorative-circle circle-2"></div>
        <div class="decorative-circle circle-3"></div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-container">
      <el-icon class="error-icon"><Warning /></el-icon>
      <p>加载学校信息失败，请稍后重试</p>
      <el-button type="primary" @click="fetchSchoolDetail">重新加载</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getSchoolDetail } from '../api/school'
import { Position, ArrowRight, Warning, Loading, Timer, Star, Medal, Link, Document, CollectionTag, Top, Trophy, Flag, Location, Briefcase } from '@element-plus/icons-vue'

const route = useRoute()
const loading = ref(true)
const school = ref(null)
const defaultLogo = 'https://via.placeholder.com/120x120?text=Logo'

// 从URL参数获取学校ID，默认使用298（西安交通大学）
const schoolId = computed(() => route.params.id || 298)

// 将学校简介按换行符分割成段落
const descriptionParagraphs = computed(() => {
  if (!school.value || !school.value.description) return ['暂无简介']
  return school.value.description.split('\n').filter(p => p.trim())
})

// 处理校徽图片加载失败
const handleLogoError = (event) => {
  event.target.src = defaultLogo
}

// 获取学校详情
const fetchSchoolDetail = async () => {
  loading.value = true
  try {
    const response = await getSchoolDetail(schoolId.value)
    console.log('Fetching school detail for ID:', schoolId.value)
    console.log('+++School detail response:', response)
    if (response.data.code === 200) {
      school.value = response.data.data
    }
  } catch (error) {
    console.error('Failed to fetch school detail:', error)
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取学校详情
onMounted(() => {
  fetchSchoolDetail()
})
</script>

<style scoped>
.school-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  position: relative;
  overflow: hidden;
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
  color: var(--accent);
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
  box-shadow: var(--shadow);
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
  background: linear-gradient(135deg, var(--accent) 0%, #764ba2 100%);
  z-index: 1;
}

.header-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0) 100%);
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
  color: var(--text-h);
  margin: 0 0 12px 0;
  letter-spacing: 1px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.school-code {
  font-size: 16px;
  color: var(--text);
  margin: 0 0 20px 0;
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

.school-location {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  color: var(--text);
  margin-top: 20px;
  background: var(--accent-bg);
  padding: 12px 20px;
  border-radius: 25px;
  width: fit-content;
  transition: all 0.3s ease;
}

.school-location:hover {
  background: var(--accent);
  color: white;
  transform: translateX(8px);
}

.location-icon {
  color: var(--accent);
  font-size: 18px;
  transition: all 0.3s ease;
}

.school-location:hover .location-icon {
  color: white;
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
  box-shadow: var(--shadow);
  display: flex;
  align-items: center;
  gap: 20px;
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
  background: var(--accent);
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
  color: var(--accent);
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
  color: var(--text-h);
  margin: 0 0 4px 0;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--text);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.website-value {
  font-size: 18px;
}

.website-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.website-link:hover {
  color: #9631e8;
  text-decoration: underline;
  transform: translateX(4px);
}

/* 详细介绍区 */
.school-description-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: var(--shadow);
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
  border-bottom: 2px solid var(--accent-bg);
}

.section-icon {
  font-size: 24px;
  color: var(--accent);
  flex-shrink: 0;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0;
  flex: 1;
}

.description-content {
  line-height: 1.8;
  font-size: 16px;
  color: var(--text);
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
  background: var(--accent);
}

.description-paragraph:last-child {
  margin-bottom: 0;
}

/* 特色标签区 */
.features-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: var(--shadow);
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
  background: var(--accent-bg);
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.feature-item:hover {
  background: white;
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.feature-icon {
  font-size: 20px;
  color: var(--accent);
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.feature-item:hover .feature-icon {
  transform: scale(1.2);
  rotate: 15deg;
}

.feature-text {
  font-size: 14px;
  color: var(--text-h);
  font-weight: 500;
  flex: 1;
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

.decorative-circle {
  position: absolute;
  border-radius: 50%;
  background: var(--accent-bg);
  opacity: 0.5;
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: 10%;
  right: -150px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: 20%;
  left: -100px;
  animation-delay: 2s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 10%;
  animation-delay: 4s;
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