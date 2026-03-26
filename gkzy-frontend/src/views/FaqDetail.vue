<template>
  <div class="faq-detail-page">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="container">
        <div class="header-left">
          <div class="logo" @click="goToHome">
            <span class="logo-icon">🎓</span>
            <span class="logo-text">高考志愿</span>
          </div>
          <nav class="nav">
            <router-link to="/" class="nav-item">首页</router-link>
            <router-link to="/schools" class="nav-item">查大学</router-link>
            <router-link to="/majors" class="nav-item">看专业</router-link>
            <router-link to="/recommendation" class="nav-item">志愿推荐</router-link>
            <router-link to="/analysis/multi-dimension" class="nav-item">多维分析</router-link>
            <router-link to="/analysis/deep-search" class="nav-item">深度检索</router-link>
          </nav>
        </div>
        <div class="header-right">
          <!-- 未登录状态 -->
          <template v-if="!isLoggedIn">
            <button class="btn btn-text" @click="handleLogin">登录</button>
            <button class="btn btn-primary" @click="handleRegister">注册</button>
          </template>
          
          <!-- 已登录状态 -->
          <template v-else>
            <div class="user-menu">
              <button class="btn btn-text user-info-btn">
                <span class="username">{{ userInfo?.username || '用户' }}</span>
                <i class="fas fa-chevron-down"></i>
              </button>
              <div class="user-dropdown">
                <div class="dropdown-item" @click="goToProfile">
                  <i class="fas fa-user"></i>
                  <span>个人中心</span>
                </div>
                <div class="dropdown-item" @click="handleLogout">
                  <i class="fas fa-sign-out-alt"></i>
                  <span>退出登录</span>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </header>

    <!-- 返回按钮 -->
    <div class="back-button-container">
      <el-button class="back-button" @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <!-- 问题详情 -->
    <div class="faq-detail-container">
      <div class="faq-detail-card">
        <div class="faq-question-section">
          <h1 class="faq-question-title">{{ question }}</h1>
        </div>
        
        <div class="faq-answer-section">
          <div class="answer-content">
            <p>{{ answer }}</p>
          </div>
        </div>

        <!-- 相关操作 -->
        <div class="faq-actions">
          <el-button type="primary" @click="goToHome">
            <el-icon><HomeFilled /></el-icon>
            返回首页
          </el-button>
        </div>
      </div>

      <!-- 其他常见问题 -->
      <div class="other-faqs-section">
        <h2 class="section-title">其他常见问题</h2>
        <div class="other-faqs-list">
          <div 
            class="other-faq-item" 
            v-for="faq in otherFaqs" 
            :key="faq.id"
            @click="viewFaq(faq)"
          >
            <span class="faq-text">{{ faq.question }}</span>
            <el-icon class="arrow-icon"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, ArrowRight, HomeFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

// 用户登录状态
const isLoggedIn = ref(false)
const userInfo = ref(null)

// 当前问题数据
const question = ref('')
const answer = ref('')

// 其他常见问题列表
const faqs = [
  {
    id: 1,
    question: '如何使用志愿推荐功能？',
    answer: '进入志愿推荐页面，输入你的高考成绩、全省位次、所在省份和选考科目，系统会根据大数据分析为你推荐冲、稳、保三个梯度的院校专业组合。'
  },
  {
    id: 2,
    question: '如何查看学校的录取分数线？',
    answer: '在高校详情页面的"录取分析"标签中，可以查看该校近 3 年的录取分数线、位次变化趋势，支持按省份、科类、批次进行筛选，帮助你更好地评估录取概率。'
  },
  {
    id: 3,
    question: '可以对比多所高校吗？',
    answer: '可以。在高校详情页面点击"加入对比"，可以同时对比多所高校，系统会为你展示详细的对比分析报告。'
  },
  {
    id: 4,
    question: '如何查看历年分数线？',
    answer: '在高校详情页面的"录取分析"标签中，可以查看该校近 3 年的录取分数线、位次变化趋势，帮助你更好地评估录取概率。'
  },
  {
    id: 5,
    question: '平台是否提供一对一咨询服务？',
    answer: '我们提供在线客服支持和专业的填报指南。对于复杂的个性化问题，可以联系我们的专业顾问团队获得一对一的咨询服务。'
  },
  {
    id: 6,
    question: '如何收藏喜欢的学校和专业？',
    answer: '登录后，在学校或专业详情页点击"收藏"按钮即可添加到个人收藏。你可以在个人中心的"我的收藏"中查看所有收藏的学校和专业。'
  }
]

// 过滤掉当前问题，显示其他问题
const otherFaqs = computed(() => {
  const currentId = parseInt(route.query.id)
  return faqs.filter(faq => faq.id !== currentId)
})

// 检查登录状态
const checkLoginStatus = () => {
  const token = localStorage.getItem('userToken')
  if (token) {
    isLoggedIn.value = true
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      userInfo.value = {
        username: payload.username,
        role: payload.role
      }
    } catch (error) {
      console.error('解析 token 失败:', error)
    }
  } else {
    isLoggedIn.value = false
    userInfo.value = null
  }
}

// 页面加载时获取问题数据
onMounted(() => {
  checkLoginStatus()
  loadFaqFromQuery()
})

// 监听路由变化，当 URL 参数改变时更新问题数据
watch(() => route.query, () => {
  loadFaqFromQuery()
})

// 从 URL 参数中加载问题数据
const loadFaqFromQuery = () => {
  question.value = route.query.question || '问题详情'
  answer.value = route.query.answer || '暂无详细解答'
}

// 导航函数
const goToHome = () => {
  router.push('/')
}

const goBack = () => {
  router.back()
}

const handleLogin = () => {
  router.push('/login')
}

const handleRegister = () => {
  router.push('/register')
}

const goToProfile = () => {
  router.push('/profile')
}

const handleLogout = () => {
  localStorage.removeItem('userToken')
  localStorage.removeItem('adminToken')
  isLoggedIn.value = false
  userInfo.value = null
  router.push('/')
  window.location.reload()
}

const viewFaq = (faq) => {
  router.push({
    path: '/faq',
    query: {
      id: faq.id,
      question: faq.question,
      answer: faq.answer
    }
  })
}
</script>

<style scoped>
.faq-detail-page {
  min-height: 100vh;
  background: #fafbfc;
}

/* ===== 导航栏 ===== */
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
  color: #333;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s;
  position: relative;
  padding: 8px 0;
}

.nav-item:hover {
  color: #1e88e5;
}

.nav-item.active {
  color: #1e88e5;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -8px;
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

.btn {
  padding: 10px 18px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-text {
  background: transparent;
  color: #666;
}

.btn-text:hover {
  color: #1e88e5;
}

.btn-primary {
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
}

.user-menu {
  position: relative;
  display: inline-block;
}

.user-info-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-weight: 500;
  color: #1e88e5;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 140px;
  padding: 8px 0;
  margin-top: 8px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.3s ease;
}

.user-menu:hover .user-dropdown {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  cursor: pointer;
  transition: all 0.2s;
  color: #333;
}

.dropdown-item:hover {
  background: #f5f5f5;
}

/* ===== 返回按钮 ===== */
.back-button-container {
  max-width: 1200px;
  margin: 20px auto 0;
  padding: 0 20px;
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

/* ===== 问题详情 ===== */
.faq-detail-container {
  max-width: 1000px;
  margin: 40px auto 80px;
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.faq-detail-card {
  background: white;
  border-radius: 16px;
  padding: 48px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
}

.faq-question-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid #e3f2fd;
}

.faq-question-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.4;
}

.faq-answer-section {
  margin-bottom: 40px;
}

.answer-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
}

.answer-content p {
  margin: 0;
  padding: 20px;
  background: #f9fafb;
  border-radius: 12px;
  border-left: 4px solid #1e88e5;
}

.faq-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.faq-actions .el-button {
  padding: 12px 32px;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 8px;
}

/* ===== 其他常见问题 ===== */
.other-faqs-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
}

.section-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 24px 0;
  padding-bottom: 16px;
  border-bottom: 2px solid #e3f2fd;
}

.other-faqs-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.other-faq-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f9fafb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.other-faq-item:hover {
  background: #e3f2fd;
  border-color: #90caf9;
  transform: translateX(8px);
}

.faq-text {
  font-size: 15px;
  color: #333;
  font-weight: 500;
  flex: 1;
}

.arrow-icon {
  color: #1e88e5;
  font-size: 18px;
  transition: all 0.3s ease;
}

.other-faq-item:hover .arrow-icon {
  transform: translateX(4px);
}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
  .header .container {
    height: 56px;
  }

  .header-left {
    gap: 20px;
  }

  .nav {
    display: none;
  }

  .faq-detail-card {
    padding: 32px 24px;
  }

  .faq-question-title {
    font-size: 22px;
  }

  .faq-actions {
    flex-direction: column;
  }

  .faq-actions .el-button {
    width: 100%;
    justify-content: center;
  }

  .other-faqs-section {
    padding: 24px;
  }
}
</style>
