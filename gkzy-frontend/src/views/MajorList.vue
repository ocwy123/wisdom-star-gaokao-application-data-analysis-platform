<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElLoading } from 'element-plus'
import { getMajorList } from '../api/major'

const router = useRouter()
const majorList = ref([])
const total = ref(0)
const loading = ref(false)
const searchKeyword = ref('')
const miniSearch = ref('')
const pagination = ref({
  page: 1,
  size: 20
})

// 用户登录状态
const isLoggedIn = ref(false)
const userInfo = ref(null)

// 检查登录状态
const checkLoginStatus = () => {
  const token = localStorage.getItem('userToken')
  if (token) {
    isLoggedIn.value = true
    // 解析JWT token获取用户信息（这里简化处理）
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      userInfo.value = {
        username: payload.username,
        role: payload.role
      }
    } catch (error) {
      console.error('解析token失败:', error)
    }
  } else {
    isLoggedIn.value = false
    userInfo.value = null
  }
}

// 初始化时检查登录状态
onMounted(() => {
  checkLoginStatus()
  loadMajors()
})

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleMiniSearch = () => {
  if (miniSearch.value.trim()) {
    // 这里可以添加全局搜索逻辑
    console.log('搜索关键词:', miniSearch.value)
  }
}

const handleLogin = () => {
  console.log('登录按钮被点击')
  // 跳转到登录页面
  router.push('/login').then(() => {
    console.log('成功跳转到登录页面')
  }).catch(err => {
    console.error('跳转失败:', err)
  })
}

const handleRegister = () => {
  console.log('注册按钮被点击')
  // 跳转到注册页面（即使已登录也可以访问）
  router.push('/register').then(() => {
    console.log('成功跳转到注册页面')
  }).catch(err => {
    console.error('跳转失败:', err)
  })
}

const handleLogout = () => {
  console.log('退出登录')
  // 清除本地存储的 token
  localStorage.removeItem('userToken')
  localStorage.removeItem('adminToken')
  
  // 更新登录状态
  isLoggedIn.value = false
  userInfo.value = null
  
  // 跳转到首页
  router.push('/').then(() => {
    console.log('退出登录成功，跳转到首页')
    // 刷新页面以更新状态
    window.location.reload()
  })
}

const goToProfile = () => {
  console.log('跳转到个人中心')
  router.push('/profile').then(() => {
    console.log('成功跳转到个人中心')
  }).catch(err => {
    console.error('跳转失败:', err)
  })
}

const loadMajors = async () => {
  const loadingInstance = ElLoading.service({ fullscreen: true, text: '加载中...' })
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      size: pagination.value.size
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    const res = await getMajorList(params)
    majorList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error('加载专业列表失败', error)
  } finally {
    loading.value = false
    loadingInstance.close()
  }
}

const viewDetail = (id) => {
  router.push(`/major/${id}?from=majors`)
}

const handleSearch = () => {
  pagination.value.page = 1
  loadMajors()
}

const handlePageChange = (page) => {
  pagination.value.page = page
  loadMajors()
}

onMounted(() => {
  loadMajors()
})

watch(() => pagination.value.page, loadMajors)
</script>

<template>
  <div class="major-list-container">
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
            <router-link to="/majors" class="nav-item active">看专业</router-link>
            <router-link to="/recommendation" class="nav-item">志愿推荐</router-link>
            <router-link to="/analysis/multi-dimension" class="nav-item">多维分析</router-link>
            <router-link to="/analysis/deep-search" class="nav-item">深度检索</router-link>
          </nav>
        </div>
        <div class="header-right">
          <button v-if="!isLoggedIn" class="btn btn-text" @click="handleLogin">登录</button>
          <button class="btn btn-primary" @click="handleRegister">注册</button>
          
          <!-- 已登录状态 -->
          <div v-if="isLoggedIn" class="user-menu">
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
        </div>
      </div>
    </header>

    <!-- Hero 区域 -->
    <div class="hero-section">
      <div class="container">
        <div class="hero-content">
          <h1>
            专业库
            <span class="count-badge">{{ total }}+ 个专业</span>
          </h1>
          <p class="subtitle">全国高校专业信息查询与深度分析，助你科学选择未来方向</p>
        </div>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-wrapper">
      <div class="custom-search">
        <div class="search-input-container">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="输入专业名称或代码"
            class="search-input-field"
            @keyup.enter="handleSearch"
          />
          <button class="search-btn" @click="handleSearch" :disabled="loading">
            <i class="fas fa-search"></i> 搜索
          </button>
        </div>
      </div>
    </div>

    <!-- 列表区域 -->
    <div class="list-section">
      <!-- 空状态 -->
      <el-empty v-if="!loading && majorList.length === 0" description="暂无专业数据" />

      <!-- 专业卡片网格 -->
      <el-row v-else :gutter="20" class="major-grid">
        <el-col
          v-for="major in majorList"
          :key="major.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card
            class="major-card"
            :body-style="{ padding: '0px' }"
            shadow="hover"
            @click="viewDetail(major.id)"
          >
            <div class="card-header">
              <div class="title-wrapper">
                <h3>{{ major.name }}</h3>
                <el-tag size="small" type="info" effect="plain">{{ major.code }}</el-tag>
              </div>
              <i class="fas fa-chevron-right arrow"></i>
            </div>
            <div class="card-body">
              <div class="major-meta">
                <span><i class="far fa-clock"></i> {{ major.duration }}年制</span>
                <span v-if="major.degree"><i class="fas fa-graduation-cap"></i> {{ major.degree }}</span>
              </div>
            </div>
            <div class="card-footer" v-if="major.subjects">
              <el-tag size="small" type="success" effect="light">
                <i class="fas fa-flask"></i> {{ major.subjects }}
              </el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 分页 -->
      <div v-if="total > pagination.size" class="pagination-wrapper">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pagination.size"
          :current-page="pagination.page"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ===== 全局容器 ===== */
.major-list-container {
  min-height: 100vh;
  background: #f8fafc;
}

/* ===== 顶部导航 ===== */
.header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  width: 100%;
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

/* 用户菜单样式 */
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
  z-index: 1000;
}

.user-menu:hover .user-dropdown {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  color: #666;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
  color: #1e88e5;
}

.dropdown-item i {
  width: 16px;
  text-align: center;
}

/* ===== Hero 区域 ===== */
.hero-section {
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  padding: 60px 0;
  color: white;
  text-align: center;
}

.hero-content h1 {
  font-size: 2.4rem;
  margin: 0 0 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  color: #ffffff;
  font-weight: 600;
  letter-spacing: -0.5px;
}

.count-badge {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 50px;
  padding: 4px 12px;
  font-size: 0.9rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.hero-content .subtitle {
  font-size: 0.95rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.4;
  font-weight: 400;
}

/* ===== 搜索栏 ===== */
 .search-wrapper {
   margin: -30px auto 50px;
   max-width: 600px;
   position: relative;
   z-index: 10;
 }

 .custom-search {
   width: 100%;
 }

 .search-input-container {
   display: flex;
   align-items: center;
   background: white;
   border-radius: 24px;
   box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
   border: 1px solid #e0e0e0;
   overflow: hidden;
   transition: all 0.3s ease;
   height: 44px;
 }

 .search-input-container:hover {
   box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
   border-color: #1e88e5;
 }

 .search-input-container:focus-within {
   box-shadow: 0 6px 25px rgba(30, 136, 229, 0.2);
   border-color: #1e88e5;
 }

 .search-icon {
   padding: 0 12px;
   color: #999;
   font-size: 14px;
 }

 .search-input-field {
  flex: 1;
  border: none;
  outline: none;
  padding: 0 20px;
  font-size: 15px;
  color: #333;
  background: transparent;
  height: 100%;
  font-weight: 400;
  letter-spacing: 0.2px;
}

.search-input-field::placeholder {
  color: #999;
  font-weight: 400;
  letter-spacing: 0.2px;
}

.search-btn {
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  color: white;
  border: none;
  padding: 0 24px;
  height: 100%;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.5px;
}

 .search-btn:hover:not(:disabled) {
   transform: translateY(-1px);
   box-shadow: 0 4px 15px rgba(30, 136, 229, 0.4);
 }

 .search-btn:disabled {
   opacity: 0.6;
   cursor: not-allowed;
 }

/* ===== 列表区域 ===== */
.list-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px 60px;
}

.major-grid {
  margin-bottom: 40px;
}

.major-grid .el-col {
  margin-bottom: 30px;
}

.major-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 20px;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
}

.major-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  border-color: #e0e0e0;
}

.card-header {
  padding: 20px 20px 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #f8f8f8;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f4f8 100%);
}

.title-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.title-wrapper h3 {
  font-size: 1.3rem;
  margin: 0;
  color: #1e3a8a;
  font-weight: 700;
  line-height: 1.2;
}

.title-wrapper .el-tag {
  font-size: 0.85rem;
  font-weight: 500;
  padding: 4px 10px;
  align-self: center;
  margin: 0 auto;
}

.arrow {
  color: #1e88e5;
  font-size: 1.3rem;
  opacity: 0.6;
  transition: all 0.3s ease;
  margin-top: 4px;
}

.major-card:hover .arrow {
  opacity: 1;
  transform: translateX(3px);
}

.card-body {
   padding: 16px 20px;
   flex: 1;
   display: flex;
   align-items: center;
   justify-content: flex-start;
 }

 .major-meta {
   display: flex;
   flex-direction: column;
   gap: 10px;
   font-size: 0.9rem;
   color: #666;
   width: 100%;
 }

 .major-meta span {
   display: flex;
   align-items: center;
   gap: 6px;
   padding: 4px 0;
 }

 .major-meta i {
   color: #1e88e5;
   width: 18px;
   font-size: 1rem;
 }

.card-footer {
  padding: 12px 20px;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  border-top: 1px solid #f0f0f0;
  overflow: hidden;
}

.card-footer .el-tag {
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
  font-size: 0.8rem;
  padding: 3px 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
  .header .container {
    height: auto;
    padding: 12px 16px;
    flex-direction: column;
    gap: 12px;
  }

  .header-left {
    width: 100%;
    gap: 16px;
  }

  .logo-text {
    font-size: 17px;
  }

  .nav {
    gap: 16px;
    font-size: 14px;
  }

  .header-right {
    width: 100%;
    gap: 8px;
  }

  .search-mini {
    flex: 1;
  }

  .btn {
    flex: 1;
    padding: 8px 14px;
    font-size: 14px;
  }

  .hero-section {
    padding: 60px 0;
  }

  .hero-content h1 {
    font-size: 2.5rem;
    gap: 12px;
  }

  .count-badge {
    font-size: 1rem;
    padding: 6px 16px;
  }

  .hero-content .subtitle {
    font-size: 1.1rem;
  }

  .search-wrapper {
    margin-top: -30px;
    padding: 0 20px;
  }

  .major-card .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .major-meta {
    flex-direction: column;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .hero-content h1 {
    font-size: 2rem;
  }

  .hero-content .subtitle {
    font-size: 1rem;
  }

  .search-mini {
    display: none;
  }
}
</style>