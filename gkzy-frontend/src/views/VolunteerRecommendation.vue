<template>
  <div class="volunteer-recommendation-page">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="container">
        <div class="header-left">
          <div class="logo" @click="scrollToTop">
            <span class="logo-icon">🎓</span>
            <span class="logo-text">高考志愿</span>
          </div>
          <nav class="nav">
            <router-link to="/" class="nav-item">首页</router-link>
            <router-link to="/schools" class="nav-item">查大学</router-link>
            <router-link to="/majors" class="nav-item">看专业</router-link>
            <router-link to="/recommendation" class="nav-item active">志愿推荐</router-link>
            <router-link to="/data" class="nav-item">数据分析</router-link>
          </nav>
        </div>
        <div class="header-right">
          <div class="search-mini">
            <input type="text" placeholder="搜索..." class="search-mini-input" v-model="miniSearch" @keyup.enter="handleSearch">
            <span class="search-icon">🔍</span>
          </div>
          <button class="btn btn-text">登录</button>
          <button class="btn btn-primary">注册</button>
        </div>
      </div>
    </header>

    <!-- 主体内容 -->
    <main class="main-content">
      <div class="container">
        <!-- 页面标题 -->
        <div class="page-header">
          <h1 class="page-title">智能志愿推荐</h1>
          <p class="page-subtitle">基于算法和历年录取数据，精准预测录取概率</p>
        </div>

        <!-- 推荐表单 -->
        <div class="recommendation-form">
          <div class="form-card">
            <div class="form-header">
              <h2 class="form-title">填写基本信息</h2>
              <p class="form-desc">系统将基于你的高考信息和院校特征，预测录取概率并推荐最适合的志愿</p>
            </div>

            <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="高考分数" prop="score">
                    <el-input-number
                      v-model="form.score"
                      :min="0"
                      :max="750"
                      :precision="0"
                      controls-position="right"
                      placeholder="请输入高考分数"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="高考位次" prop="rank">
                    <el-input-number
                      v-model="form.rank"
                      :min="1"
                      :max="1000000"
                      :precision="0"
                      controls-position="right"
                      placeholder="请输入高考位次（可选）"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="所在省份" prop="province">
                    <el-select
                      v-model="form.province"
                      placeholder="请选择省份"
                      filterable
                      style="width: 100%"
                    >
                      <el-option
                        v-for="province in provinces"
                        :key="province"
                        :label="province"
                        :value="province"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="选科类别" prop="subject">
                    <el-select
                      v-model="form.subject"
                      placeholder="请选择选科类别"
                      style="width: 100%"
                    >
                      <el-option label="物理类" value="物理类" />
                      <el-option label="历史类" value="历史类" />
                      <el-option label="理科" value="理科" />
                      <el-option label="文科" value="文科" />
                      <el-option label="综合类" value="综合类" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-divider>理想院校偏好（可选）</el-divider>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="理想省份">
                    <el-select
                      v-model="form.school_province"
                      placeholder="请选择理想院校省份"
                      filterable
                      clearable
                      style="width: 100%"
                    >
                      <el-option
                        v-for="province in provinces"
                        :key="province"
                        :label="province"
                        :value="province"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="院校类型">
                    <el-select
                      v-model="form.school_type"
                      placeholder="请选择理想院校类型"
                      clearable
                      style="width: 100%"
                    >
                      <el-option label="理工类" value="理工类" />
                      <el-option label="财经类" value="财经类" />
                      <el-option label="综合类" value="综合类" />
                      <el-option label="师范类" value="师范类" />
                      <el-option label="农林类" value="农林类" />
                      <el-option label="医药类" value="医药类" />
                      <el-option label="艺术类" value="艺术类" />
                      <el-option label="语言类" value="语言类" />
                      <el-option label="政法类" value="政法类" />
                      <el-option label="体育类" value="体育类" />
                      <el-option label="民族类" value="民族类" />
                      <el-option label="军事类" value="军事类" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <div class="form-actions">
                <el-button
                  type="primary"
                  size="large"
                  :loading="loading"
                  @click="handleRecommendation"
                >
                  开始推荐
                </el-button>
                <el-button size="large" @click="resetForm">重置</el-button>
              </div>
            </el-form>
          </div>
        </div>

        <!-- 推荐结果 -->
        <div v-if="recommendationResult" class="recommendation-result">
          <div class="result-card">
            <div class="result-header">
              <h2 class="result-title">推荐结果</h2>
              <p class="result-desc">基于你的分数和偏好，为你推荐以下院校</p>
            </div>

            <!-- 冲刺院校 -->
            <div class="result-section">
              <div class="section-header">
                <div class="section-title-group">
                  <h3 class="section-title">
                    <span class="title-icon">🚀</span>
                    冲刺院校 ({{ recommendationResult.rush.length }}所)
                  </h3>
                </div>
              </div>
              <div class="school-grid">
                <div
                  v-for="school in recommendationResult.rush"
                  :key="school.id"
                  class="school-card rush-card"
                  @click="goToSchoolDetail(school.id)"
                >
                  <div class="school-header">
                    <div class="school-logo" v-if="school.logo">
                      <img :src="school.logo" :alt="school.name" />
                    </div>
                    <div class="school-logo-placeholder" v-else>
                      <span>{{ school.name.charAt(0) }}</span>
                    </div>
                    <div class="school-info">
                      <h4 class="school-name">{{ school.name }}</h4>
                      <p class="school-location">
                        <el-icon><Location /></el-icon>
                        {{ school.province }} · {{ school.city }}
                      </p>
                    </div>
                  </div>

                  <div class="school-tags">
                    <el-tag v-if="school.is_985" type="danger" size="small" effect="plain">985</el-tag>
                    <el-tag v-if="school.is_211" type="warning" size="small" effect="plain">211</el-tag>
                    <el-tag v-if="school.is_double_first" type="success" size="small" effect="plain">双一流</el-tag>
                    <el-tag type="info" size="small" effect="plain">{{ school.type }}</el-tag>
                  </div>

                  <div class="school-stats">
                    <div class="stat-item">
                      <span class="stat-label">录取概率</span>
                      <span class="stat-value probability">{{ (school.probability * 100).toFixed(1) }}%</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">历年平均分</span>
                      <span class="stat-value">{{ school.avg_score.toFixed(0) }}</span>
                    </div>
                  </div>

                  <div class="school-footer">
                    <span class="view-detail">查看详情 →</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 稳妥院校 -->
            <div class="result-section">
              <div class="section-header">
                <div class="section-title-group">
                  <h3 class="section-title">
                    <span class="title-icon">✅</span>
                    稳妥院校 ({{ recommendationResult.stable.length }}所)
                  </h3>
                </div>
              </div>
              <div class="school-grid">
                <div
                  v-for="school in recommendationResult.stable"
                  :key="school.id"
                  class="school-card stable-card"
                  @click="goToSchoolDetail(school.id)"
                >
                  <div class="school-header">
                    <div class="school-logo" v-if="school.logo">
                      <img :src="school.logo" :alt="school.name" />
                    </div>
                    <div class="school-logo-placeholder" v-else>
                      <span>{{ school.name.charAt(0) }}</span>
                    </div>
                    <div class="school-info">
                      <h4 class="school-name">{{ school.name }}</h4>
                      <p class="school-location">
                        <el-icon><Location /></el-icon>
                        {{ school.province }} · {{ school.city }}
                      </p>
                    </div>
                  </div>

                  <div class="school-tags">
                    <el-tag v-if="school.is_985" type="danger" size="small" effect="plain">985</el-tag>
                    <el-tag v-if="school.is_211" type="warning" size="small" effect="plain">211</el-tag>
                    <el-tag v-if="school.is_double_first" type="success" size="small" effect="plain">双一流</el-tag>
                    <el-tag type="info" size="small" effect="plain">{{ school.type }}</el-tag>
                  </div>

                  <div class="school-stats">
                    <div class="stat-item">
                      <span class="stat-label">录取概率</span>
                      <span class="stat-value probability">{{ (school.probability * 100).toFixed(1) }}%</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">历年平均分</span>
                      <span class="stat-value">{{ school.avg_score.toFixed(0) }}</span>
                    </div>
                  </div>

                  <div class="school-footer">
                    <span class="view-detail">查看详情 →</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 保底院校 -->
            <div class="result-section">
              <div class="section-header">
                <div class="section-title-group">
                  <h3 class="section-title">
                    <span class="title-icon">🛡️</span>
                    保底院校 ({{ recommendationResult.safe.length }}所)
                  </h3>
                </div>
              </div>
              <div class="school-grid">
                <div
                  v-for="school in recommendationResult.safe"
                  :key="school.id"
                  class="school-card safe-card"
                  @click="goToSchoolDetail(school.id)"
                >
                  <div class="school-header">
                    <div class="school-logo" v-if="school.logo">
                      <img :src="school.logo" :alt="school.name" />
                    </div>
                    <div class="school-logo-placeholder" v-else>
                      <span>{{ school.name.charAt(0) }}</span>
                    </div>
                    <div class="school-info">
                      <h4 class="school-name">{{ school.name }}</h4>
                      <p class="school-location">
                        <el-icon><Location /></el-icon>
                        {{ school.province }} · {{ school.city }}
                      </p>
                    </div>
                  </div>

                  <div class="school-tags">
                    <el-tag v-if="school.is_985" type="danger" size="small" effect="plain">985</el-tag>
                    <el-tag v-if="school.is_211" type="warning" size="small" effect="plain">211</el-tag>
                    <el-tag v-if="school.is_double_first" type="success" size="small" effect="plain">双一流</el-tag>
                    <el-tag type="info" size="small" effect="plain">{{ school.type }}</el-tag>
                  </div>

                  <div class="school-stats">
                    <div class="stat-item">
                      <span class="stat-label">录取概率</span>
                      <span class="stat-value probability">{{ (school.probability * 100).toFixed(1) }}%</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">历年平均分</span>
                      <span class="stat-value">{{ school.avg_score.toFixed(0) }}</span>
                    </div>
                  </div>

                  <div class="school-footer">
                    <span class="view-detail">查看详情 →</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Location } from '@element-plus/icons-vue'
import { getVolunteerRecommendation } from '../api/recommendation'

// 表单数据
const form = reactive({
  score: null,
  rank: null,
  province: '',
  subject: '',
  school_province: '',
  school_type: ''
})

// 表单验证规则
const rules = {
  score: [
    { required: true, message: '请输入高考分数', trigger: 'blur' },
    { type: 'number', min: 0, max: 750, message: '分数必须在0-750之间', trigger: 'blur' }
  ],
  province: [
    { required: true, message: '请选择所在省份', trigger: 'change' }
  ],
  subject: [
    { required: true, message: '请选择选科类别', trigger: 'change' }
  ]
}

// 响应式数据
const formRef = ref(null)
const loading = ref(false)
const recommendationResult = ref(null)
const miniSearch = ref('')

// 省份列表
const provinces = [
  '北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
  '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南',
  '湖北', '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州',
  '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆'
]

// 方法
const handleRecommendation = async () => {
  try {
    await formRef.value.validate()
  } catch (error) {
    return
  }

  loading.value = true
  try {
    const params = {
      score: form.score,
      province: form.province,
      subject: form.subject
    }

    if (form.school_province) {
      params.school_province = form.school_province
    }

    if (form.school_type) {
      params.school_type = form.school_type
    }

    const response = await getVolunteerRecommendation(params)
    console.log('API Response:', response)

    if (response.data.code === 200) {
      const result = response.data.data || { rush: [], stable: [], safe: [] }
      // 前端按录取概率升序显示
      const sortAsc = arr => arr.sort((a, b) => Number(a.probability) - Number(b.probability))
      result.rush = sortAsc(result.rush || [])
      result.stable = sortAsc(result.stable || [])
      result.safe = sortAsc(result.safe || [])
      recommendationResult.value = result
      ElMessage.success('志愿推荐成功！')
    } else {
      console.log('API Error Response:', response.data)
      ElMessage.error(response.data.message || '推荐失败，请重试')
    }
  } catch (error) {
    console.error('推荐失败:', error)
    console.error('Error response:', error.response?.data)
    ElMessage.error('推荐失败，请检查网络连接或稍后重试')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formRef.value.resetFields()
  recommendationResult.value = null
}

const goToSchoolDetail = (schoolId) => {
  window.open(`/school/${schoolId}`, '_blank')
}

const handleSearch = () => {
  if (miniSearch.value.trim()) {
    console.log('搜索:', miniSearch.value)
  }
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
})
</script>

<style scoped>
.volunteer-recommendation-page {
  min-height: 100vh;
  background: #f5f7fa;
}

/* 头部样式 */
.header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 40px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.logo:hover {
  opacity: 0.7;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav {
  display: flex;
  gap: 32px;
}

.nav-item {
  color: #666;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: color 0.2s;
  position: relative;
}

.nav-item:hover,
.nav-item.active {
  color: #1e88e5;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -21px;
  left: 0;
  width: 100%;
  height: 2px;
  background: #1e88e5;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-mini {
  position: relative;
  width: 200px;
}

.search-mini-input {
  width: 100%;
  padding: 10px 12px 10px 16px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  font-size: 14px;
  background: #f5f5f5;
  transition: all 0.2s;
}

.search-mini-input:focus {
  outline: none;
  background: white;
  border-color: #1e88e5;
  box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.1);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  font-size: 16px;
  cursor: pointer;
}

.btn {
  padding: 8px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-text {
  background: transparent;
  color: #666;
  border: 1px solid #e8e8e8;
}

.btn-text:hover {
  border-color: #1e88e5;
  color: #1e88e5;
}

.btn-primary {
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
}

/* 主体内容 */
.main-content {
  padding: 40px 0;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 12px 0;
}

.page-subtitle {
  font-size: 15px;
  color: #666;
}

/* 表单样式 */
.recommendation-form {
  margin-bottom: 40px;
}

.form-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.form-header {
  margin-bottom: 24px;
}

.form-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.form-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.form-actions {
  text-align: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e4e7ed;
}

/* 结果样式 */
.recommendation-result {
  margin-top: 40px;
}

.result-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.result-header {
  margin-bottom: 32px;
}

.result-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.result-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 结果区域 */
.result-section {
  margin-bottom: 48px;
}

.section-header {
  margin-bottom: 20px;
}

.section-title-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-title {
  display: flex;
  align-items: center;
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.title-icon {
  margin-right: 12px;
  font-size: 26px;
}

/* 学校网格 */
.school-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

/* 学校卡片 */
.school-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e4e7ed;
}

.school-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  border-color: #667eea;
}

.rush-card:hover {
  box-shadow: 0 8px 24px rgba(245, 108, 108, 0.15);
  border-color: #f56c6c;
}

.stable-card:hover {
  box-shadow: 0 8px 24px rgba(103, 194, 58, 0.15);
  border-color: #67c23a;
}

.safe-card:hover {
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.15);
  border-color: #409eff;
}

.school-header {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.school-logo {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f5f7fa;
}

.school-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.school-logo-placeholder {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.school-logo-placeholder span {
  font-size: 28px;
  font-weight: 700;
  color: white;
}

.school-info {
  flex: 1;
}

.school-name {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.school-location {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #999;
  margin: 0;
}

.school-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.school-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #667eea;
}

.probability {
  color: #f56c6c;
}

.school-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.view-detail {
  font-size: 13px;
  color: #667eea;
  font-weight: 600;
  transition: all 0.3s;
}

.school-card:hover .view-detail {
  color: #764ba2;
}

/* 响应式 */
@media (max-width: 768px) {
  .header-left {
    gap: 20px;
  }

  .nav {
    gap: 16px;
  }

  .nav-item {
    font-size: 13px;
    padding: 6px 12px;
  }

  .search-mini {
    width: 150px;
  }

  .search-mini-input:focus {
    width: 180px;
  }

  .school-grid {
    grid-template-columns: 1fr;
  }

  .form-card,
  .result-card {
    padding: 24px;
  }

  .page-title {
    font-size: 24px;
  }
}
</style>
