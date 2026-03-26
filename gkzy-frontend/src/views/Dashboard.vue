<template>
  <div class="dashboard">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="container">
        <div class="header-left">
          <div class="logo" @click="scrollToTop">
            <span class="logo-icon">🎓</span>
            <span class="logo-text">高考志愿</span>
          </div>
          <nav class="nav">
            <router-link to="/" class="nav-item active">首页</router-link>
            <router-link to="/schools" class="nav-item">查大学</router-link>
            <router-link to="/majors" class="nav-item">看专业</router-link>
            <router-link to="/志愿" class="nav-item">志愿填报</router-link>
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

    <!-- 轮播图区域 -->
    <section class="carousel-section">
      <div class="container">
        <div class="carousel-layout">
          <!-- 左侧功能模块 -->
          <div class="side-module left-module">
            <div class="module-card">
              <div class="countdown-header">
                <div class="module-icon">⏰</div>
                <h3 class="module-title">高考倒计时</h3>
              </div>
              <div class="countdown-content">
                <div class="countdown-days">
                  <span class="days-number">{{ countdownDays }}</span>
                  <span class="days-label">天</span>
                </div>
                <div class="countdown-info">
                  <p class="countdown-date">2026年6月7日</p>
                  <p class="countdown-desc">距离高考还有</p>
                </div>
              </div>
              <div class="countdown-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: countdownProgress + '%' }"></div>
                </div>
                <div class="progress-text">
                  <span>已过 {{ countdownProgress }}%</span>
                </div>
              </div>
              <div class="countdown-stats">
                <div class="stat-item">
                  <span class="stat-label">备考阶段</span>
                  <span class="stat-value">{{ getStudyPhase() }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">剩余周数</span>
                  <span class="stat-value">{{ Math.ceil(countdownDays / 7) }}周</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">建议复习</span>
                  <span class="stat-value">{{ getStudyAdvice() }}</span>
                </div>
              </div>
              <div class="countdown-motivation">
                <div class="motivation-icon">💪</div>
                <p class="motivation-text">{{ getMotivationText() }}</p>
              </div>
            </div>
          </div>

          <!-- 轮播图 -->
          <div class="carousel-main">
            <div class="carousel">
              <div
                class="carousel-item"
                v-for="(slide, index) in carouselSlides"
                :key="index"
                :class="{ active: currentSlide === index }"
              >
                <div class="slide-content" :style="{ background: slide.gradient }">
                  <div class="slide-text">
                    <div class="slide-badge">{{ slide.badge }}</div>
                    <h2 class="slide-title">{{ slide.title }}</h2>
                    <p class="slide-desc">{{ slide.description }}</p>
                    <button class="slide-btn" @click="navigateTo(slide.link)">
                      {{ slide.buttonText }} →
                    </button>
                  </div>
                </div>
              </div>
              <div class="carousel-controls">
                <button class="control-btn" @click="prevSlide">‹</button>
                <div class="carousel-dots">
                  <span
                    class="dot"
                    v-for="(slide, index) in carouselSlides"
                    :key="index"
                    :class="{ active: currentSlide === index }"
                    @click="goToSlide(index)"
                  ></span>
                </div>
                <button class="control-btn" @click="nextSlide">›</button>
              </div>
            </div>
          </div>

          <!-- 右侧功能模块 -->
          <div class="side-module right-module">
            <div class="module-card">
              <h3 class="module-title">快捷功能</h3>
              <div class="quick-functions">
                <div class="function-item" v-for="func in quickFunctions" :key="func.id" @click="navigateTo(func.route)">
                  <div class="function-content">
                    <span class="function-name">{{ func.name }}</span>
                    <span class="function-desc">{{ func.desc }}</span>
                  </div>
                  <span class="function-arrow">→</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 平台横幅 -->
    <section class="platform-banner">
      <div class="container">
        <h2 class="banner-title">高考志愿平台</h2>
      </div>
    </section>

    <!-- 热门院校 -->
    <section class="schools-section">
      <div class="container">
        <div class="section-header">
          <div class="section-title-group">
            <h2 class="section-title">热门院校</h2>
          </div>
          <div class="section-controls">
            <div class="filter-tabs">
              <button class="filter-tab" :class="{ active: schoolFilter === 'all' }" @click="schoolFilter = 'all'">全部</button>
              <button class="filter-tab" :class="{ active: schoolFilter === '985' }" @click="schoolFilter = '985'">985</button>
              <button class="filter-tab" :class="{ active: schoolFilter === '211' }" @click="schoolFilter = '211'">211</button>
              <button class="filter-tab" :class="{ active: schoolFilter === 'double' }" @click="schoolFilter = 'double'">双一流</button>
            </div>
            <a href="#" class="more-link" @click.prevent="navigateTo('/schools')">查看全部 →</a>
          </div>
        </div>
        <div class="schools-grid">
          <div
            class="school-card"
            v-for="school in filteredSchools.slice(0, 16)"
            :key="school.id"
            @click="viewSchoolDetail(school.id)"
          >
            <div class="school-logo-wrapper">
              <!-- 如果是图片 URL，显示图片；如果是 emoji，直接显示文本 -->
              <img v-if="school.logo && school.logo.startsWith('http')" 
                   :src="school.logo" 
                   :alt="school.name" 
                   class="school-logo-img" />
              <div v-else class="school-logo-emoji">{{ school.logo }}</div>
            </div>
            <div class="school-content">
              <h3 class="school-name">{{ school.name }}</h3>
              <p class="school-location">{{ school.location }}</p>
              <div class="school-footer">
                <div class="school-tags">
                  <span class="tag" v-for="tag in school.tags" :key="tag">{{ tag }}</span>
                </div>
                <span class="view-link">查看院校 →</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 热门专业 -->
    <section class="majors-section">
      <div class="container">
        <div class="section-header">
          <div class="section-title-group">
            <h2 class="section-title">热门专业</h2>
            <p class="section-subtitle">就业前景好，报考热度高</p>
          </div>
          <a href="#" class="more-link" @click.prevent="navigateTo('/majors')">查看全部 →</a>
        </div>
        <div class="majors-grid">
          <div class="major-card" v-for="major in topMajors" :key="major.id" @click="viewMajorDetail(major.id)">
            <div class="card-header">
              <div class="title-wrapper">
                <h3>{{ major.name }}</h3>
                <el-tag size="small" type="primary">{{ major.code }}</el-tag>
              </div>
              <span class="arrow">→</span>
            </div>
            <div class="card-body">
              <div class="major-meta">
                <div class="meta-item">
                  <span class="meta-label">平均薪资</span>
                  <span class="meta-value">{{ major.salary }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">修业年限</span>
                  <span class="meta-value">{{ major.duration }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 常见问题 -->
    <section class="faq-section">
      <div class="container">
        <div class="section-header">
          <div class="section-title-group">
            <h2 class="section-title">常见问题</h2>
            <p class="section-subtitle">解答你的疑惑</p>
          </div>
        </div>
        <div class="faq-grid">
          <div class="faq-item" v-for="faq in faqs" :key="faq.id" @click="viewFaqDetail(faq)">
            <div class="faq-header">
              <h3 class="faq-question">{{ faq.question }}</h3>
              <span class="faq-toggle">+</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA 区域 -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-content">
          <h2 class="cta-title">准备好开始了吗？</h2>
          <p class="cta-subtitle">立即体验，获取个性化志愿推荐方案</p>
          <button class="cta-btn" @click="navigateTo('/register')">立即体验</button>
        </div>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-col-centered">
            <h4 class="footer-title">关于我们</h4>
            <p class="footer-desc">高考志愿数据分析平台致力于为全国高考考生<br>提供最专业、最全面的志愿填报服务，<br>帮助考生科学决策。</p>
          </div>
        </div>
        <div class="footer-bottom">
          <p class="footer-copyright">© 2026 高考志愿数据分析平台</p>
        </div>
      </div>
    </footer>

    <!-- 回到顶部 -->
    <button class="back-to-top" :class="{ visible: showBackToTop }" @click="scrollToTop">↑</button>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getHotSchools, getMajorRank } from '../api/overview'

const router = useRouter()
const searchQuery = ref('')
const miniSearch = ref('')
const showBackToTop = ref(false)
const currentSlide = ref(0)
const carouselTimer = ref(null)
const schoolFilter = ref('all')

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

// 高考倒计时相关数据
const countdownDays = ref(0)
const countdownProgress = ref(0)

const quickFunctions = [
  { id: 1, icon: '🏫', name: '高校查询', desc: '2900+ 高校信息', route: '/schools' },
  { id: 2, icon: '📚', name: '专业查询', desc: '800+ 专业详情', route: '/majors' },
  { id: 3, icon: '📊', name: '分数线', desc: '3 年录取数据', route: '/scores' },
  { id: 4, icon: '🎯', name: '志愿推荐', desc: '智能匹配方案', route: '/analysis' }
]

const carouselSlides = [
  {
    badge: '智能推荐',
    title: '志愿智能分析',
    description: '基于大数据和AI算法，为你的志愿填报提供科学决策支持',
    buttonText: '立即体验',
    link: '/analysis',
    icon: '🎓',
    gradient: '#1e88e5'
  },
  {
    badge: '数据库',
    title: '高校数据库',
    description: '3000+ 所高校详细信息，5年历史录取数据，助力科学选择',
    buttonText: '查看高校',
    link: '/schools',
    icon: '🏫',
    gradient: '#f093fb'
  },
  {
    badge: '就业前景',
    title: '专业深度解析',
    description: '了解专业前景、课程设置、就业方向，做出最优选择',
    buttonText: '探索专业',
    link: '/majors',
    icon: '📚',
    gradient: '#4facfe'
  }
]

const topMajors = ref([])

const faqs = [
  {
    id: 1,
    question: '如何使用志愿推荐功能？',
    answer: '进入志愿推荐页面，输入你的高考成绩、全省位次、所在省份和选考科目，系统会根据大数据分析为你推荐冲、稳、保三个梯度的院校专业组合。'
  },
  {
    id: 2,
    question: '如何查看学校的录取分数线？',
    answer: '在高校详情页面的"录取分析"标签中，可以查看该校近5年的录取分数线、位次变化趋势，支持按省份、科类、批次进行筛选，帮助你更好地评估录取概率。'
  },
  {
    id: 3,
    question: '可以对比多所高校吗？',
    answer: '可以。在高校详情页面点击"加入对比"，最多可以同时对比 4 所高校，系统会为你展示详细的对比分析报告。'
  },
  {
    id: 4,
    question: '如何查看历年分数线？',
    answer: '在高校详情页面的"录取分析"标签中，可以查看该校近 5 年的录取分数线、位次变化趋势，帮助你更好地评估录取概率。'
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

const recommendedSchools = ref([])

// 根据筛选条件过滤学校
const filteredSchools = computed(() => {
  if (schoolFilter.value === 'all') {
    return recommendedSchools.value
  } else if (schoolFilter.value === '985') {
    return recommendedSchools.value.filter(school => school.is_985)
  } else if (schoolFilter.value === '211') {
    return recommendedSchools.value.filter(school => school.is_211)
  } else if (schoolFilter.value === 'double') {
    return recommendedSchools.value.filter(school => school.is_double_first)
  }
  return recommendedSchools.value
})

onMounted(async () => {
  checkLoginStatus()
  setupScrollListener()
  startCarousel()
  setupCountdown()
  await loadHotSchools()
  await loadTopMajors()
})

onUnmounted(() => {
  removeScrollListener()
  stopCarousel()
})

async function loadHotSchools() {
  try {
    const res = await getHotSchools({ limit: 12 })
    if (res.data && res.data.length > 0) {
      recommendedSchools.value = res.data.map(school => {
        let location = `${school.province || ''}${school.city || ''}`.replace(/(省|市)/g, '')
        const municipalities = ['北京', '上海', '天津', '重庆']
        municipalities.forEach(city => {
          if (location.startsWith(city) && location !== city) {
            location = city
          }
        })
        
        const tags = getSchoolTags(school)
        
        return {
          ...school,
          location,
          level: school.is_985 ? '985' : school.is_211 ? '211' : '一本',
          // 使用数据库中的 logo，如果没有则使用 emoji
          logo: school.logo || getSchoolLogo(school.type),
          tags: tags,
          heatScore: Math.round(school.heat_score || 0)
        }
      })
    }
  } catch (error) {
    console.error('加载热门院校失败', error)
  }
}

async function loadTopMajors() {
  try {
    const res = await getMajorRank({ limit: 6 })
    
    let majorsData = []
    if (res && res.data && Array.isArray(res.data)) {
      majorsData = res.data
    } else if (res && Array.isArray(res)) {
      majorsData = res
    }
    
    if (majorsData && majorsData.length > 0) {
      topMajors.value = majorsData.map(major => {
        return {
          id: major.id,
          name: major.name,
          code: major.code || '',
          salary: formatSalary(major.avg_salary),
          duration: major.duration || '四年'
        }
      })
    }
  } catch (error) {
    console.error('加载热门专业失败:', error)
  }
}

function getMajorIcon(majorName) {
  const iconMap = {
    '计算机': '💻',
    '软件': '💻',
    '临床': '🏥',
    '医学': '🏥',
    '金融': '💰',
    '经济': '💰',
    '机械': '⚙️',
    '师范': '📚',
    '教育': '📚',
    '生物': '🌿',
    '电气': '⚡',
    '土木': '🏗️',
    '化学': '🧪',
    '物理': '🔬',
    '数学': '📐',
    '外语': '🌍',
    '艺术': '🎨',
    '体育': '⚽',
    '农业': '🌾'
  }
  
  for (const [key, icon] of Object.entries(iconMap)) {
    if (majorName.includes(key)) {
      return icon
    }
  }
  return '🎓'
}

function getMajorBadge(salary) {
  if (salary >= 15000) return '高薪'
  if (salary >= 12000) return '热门'
  if (salary >= 10000) return '稳定'
  return '潜力'
}

function formatSalary(salary) {
  if (!salary) return '面议'
  const k = Math.floor(salary / 1000)
  return `${k}k`
}

function getSchoolLogo(type) {
  const logos = {
    '综合': '🏛️',
    '理工': '⚡',
    '师范': '📚',
    '财经': '💰',
    '医学': '🏥',
    '农业': '🌾',
    '艺术': '🎨',
    '体育': '⚽'
  }
  return logos[type] || '🏫'
}

function getSchoolTags(school) {
  // 只保留一个类别标签，优先显示学校类型
  if (school.type) {
    return [school.type]
  }
  // 如果没有类型，则显示985/211标签
  if (school.is_985) return ['985']
  if (school.is_211) return ['211']
  return []
}

function startCarousel() {
  carouselTimer.value = setInterval(() => {
    nextSlide()
  }, 5000)
}

function stopCarousel() {
  if (carouselTimer.value) clearInterval(carouselTimer.value)
}

function nextSlide() {
  currentSlide.value = (currentSlide.value + 1) % carouselSlides.length
}

function prevSlide() {
  currentSlide.value = (currentSlide.value - 1 + carouselSlides.length) % carouselSlides.length
}

function goToSlide(index) {
  currentSlide.value = index
}

function setupScrollListener() {
  window.addEventListener('scroll', handleScroll)
}

function removeScrollListener() {
  window.removeEventListener('scroll', handleScroll)
}

function handleScroll() {
  showBackToTop.value = window.scrollY > 300
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleSearch() {
  const query = searchQuery.value || miniSearch.value
  if (query.trim()) {
    router.push(`/search?q=${encodeURIComponent(query)}`)
  }
}

function quickSearch(tag) {
  searchQuery.value = tag
  handleSearch()
}

function navigateTo(route) {
  router.push(route)
}

function viewFaqDetail(faq) {
  console.log('查看 FAQ 详情:', faq)
  router.push({
    path: '/faq',
    query: {
      id: faq.id,
      question: faq.question,
      answer: faq.answer
    }
  }).then(() => {
    console.log('成功跳转到 FAQ 详情页')
  }).catch(err => {
    console.error('跳转失败:', err)
  })
}

// 登录注册相关函数
function handleLogin() {
  console.log('登录按钮被点击')
  // 跳转到登录页面
  router.push('/login').then(() => {
    console.log('成功跳转到登录页面')
  }).catch(err => {
    console.error('跳转失败:', err)
  })
}

function handleRegister() {
  console.log('注册按钮被点击')
  // 跳转到注册页面（即使已登录也可以访问）
  router.push('/register').then(() => {
    console.log('成功跳转到注册页面')
  }).catch(err => {
    console.error('跳转失败:', err)
  })
}

function goToProfile() {
  console.log('跳转到个人中心')
  router.push('/profile').then(() => {
    console.log('成功跳转到个人中心')
  }).catch(err => {
    console.error('跳转失败:', err)
  })
}

function handleLogout() {
  console.log('退出登录')
  // 清除本地存储的token
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

function viewSchoolDetail(id) {
  router.push(`/school/${id}`)
}

function viewMajorDetail(id) {
  router.push(`/major/${id}?from=home`)
}

function setupCountdown() {
  // 设置高考日期为2026年6月7日
  const gaokaoDate = new Date(2026, 5, 7) // 月份从0开始，5代表6月
  const today = new Date()
  
  // 计算剩余天数
  const timeDiff = gaokaoDate.getTime() - today.getTime()
  const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24))
  
  countdownDays.value = daysDiff > 0 ? daysDiff : 0
  
  // 计算进度（假设备考周期为365天）
  const totalDays = 365
  const passedDays = totalDays - daysDiff
  countdownProgress.value = Math.max(0, Math.min(100, Math.round((passedDays / totalDays) * 100)))
}

function getStudyPhase() {
  const days = countdownDays.value
  if (days > 180) return '基础阶段'
  if (days > 90) return '强化阶段'
  if (days > 30) return '冲刺阶段'
  return '最后冲刺'
}

function getStudyAdvice() {
  const days = countdownDays.value
  if (days > 180) return '夯实基础'
  if (days > 90) return '专题突破'
  if (days > 30) return '模拟训练'
  return '查漏补缺'
}

function getMotivationText() {
  const days = countdownDays.value
  if (days > 180) return '千里之行，始于足下！'
  if (days > 90) return '坚持就是胜利，加油！'
  if (days > 30) return '胜利在望，坚持到底！'
  return '相信自己，你一定行！'
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.dashboard {
  min-height: 100vh;
  background: #fafbfc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
  -webkit-font-smoothing: antialiased;
  color: #1a1a1a;
  width: 100%;
  margin: 0;
  padding: 0;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  width: 100%;
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
  background: #1e88e5;
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
  box-shadow: 0 2px 8px rgba(30, 136, 229, 0.1);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  pointer-events: none;
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
  color: #1a1a1a;
  background: #f0f0f0;
}

.btn-primary {
  background: #1e88e5;
  color: white;
  box-shadow: 0 2px 8px rgba(30, 136, 229, 0.2);
}

.btn-primary:hover {
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

/* ===== Hero 搜索区域 ===== */
.hero-section {
  background: #1e88e5;
  padding: 60px 0;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: -40%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  color: white;
  margin: 0 0 16px 0;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 32px 0;
  line-height: 1.5;
}

.hero-search {
  max-width: 700px;
  margin: 0 auto;
}

.search-container {
  display: flex;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  margin-bottom: 16px;
}

.search-input {
  flex: 1;
  padding: 14px 18px;
  border: none;
  outline: none;
  font-size: 15px;
}

.search-btn {
  padding: 14px 32px;
  background: #1e88e5;
  border: none;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.search-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
}

.search-suggestions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.suggestion-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  font-weight: 500;
}

.suggestion-tag {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.15);
  transition: all 0.2s;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.suggestion-tag:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
}

/* ===== 平台横幅 ===== */
.platform-banner {
  padding: 20px 0;
  background: #1e88e5;
  margin-top: 16px;
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.2);
}

.banner-title {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin: 0;
  text-align: center;
  letter-spacing: 2px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* ===== 数据概览 ===== */
.stats-section {
  padding: 40px 0;
  background: white;
  margin-top: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.stat-card {
  background: #f5f7fa;
  padding: 32px 24px;
  border-radius: 12px;
  text-align: center;
  transition: all 0.2s;
  border: 1px solid rgba(30, 136, 229, 0.1);
}

.stat-card:nth-child(2) {
  background: #fa709a;
}

.stat-card:nth-child(3) {
  background: #30cfd0;
}

.stat-card:nth-child(4) {
  background: #a8edea;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(30, 136, 229, 0.15);
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: white;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 4px;
}

.stat-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

/* ===== 轮播图 ===== */
/* ===== 轮播图 ===== */
.carousel-section {
  padding: 40px 0;
  background: #f8f9fa;
}

.carousel-layout {
  display: grid;
  grid-template-columns: 200px 1fr 200px;
  gap: 16px;
  align-items: stretch;  /* 改为 stretch，让所有列对齐 */
}

.side-module {
  height: auto;
}

.module-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  height: 100%;
  min-height: 320px;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.module-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.module-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

/* 高考倒计时样式 */
.countdown-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;  /* 减少间距 */
}

.countdown-content {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;  /* 减少间距 */
}

.countdown-days {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.days-number {
  font-size: 32px;
  font-weight: 700;
  color: #ff6b6b;
  line-height: 1;
}

.days-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.countdown-info {
  flex: 1;
}

.countdown-date {
  font-size: 12px;
  color: #666;
  margin: 0 0 4px 0;
  font-weight: 500;
}

.countdown-desc {
  font-size: 11px;
  color: #999;
  margin: 0;
}

.countdown-progress {
  margin-top: 12px;  /* 减少间距 */
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;  /* 减少间距 */
}

.progress-fill {
  height: 100%;
  background: #ff6b6b;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 10px;
  color: #999;
  text-align: center;
}

.countdown-stats {
  margin-top: 12px;  /* 减少间距 */
  padding-top: 12px;  /* 减少间距 */
  border-top: 1px solid #f0f0f0;
  flex: 1;  /* 让统计信息占据剩余空间 */
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;  /* 减少间距 */
}

.stat-item:last-child {
  margin-bottom: 0;
}

.stat-label {
  font-size: 11px;
  color: #666;
}

.stat-value {
  font-size: 11px;
  font-weight: 600;
  color: #ff6b6b;
  background: #fff5f5;
  padding: 2px 6px;
  border-radius: 3px;
}

.countdown-motivation {
  margin-top: auto;  /* 推到底部 */
  padding: 12px 12px 12px 8px;  /* 左内边距减少，文字向左偏移 */
  background: #fff5f5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid #ff6b6b;
  border-left: 3px solid #ff6b6b;
}

.motivation-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.motivation-text {
  font-size: 11px;
  color: #ff6b6b;
  font-weight: 500;
  margin: 0;
  line-height: 1.4;
  white-space: nowrap;
}

/* 快捷功能样式 */
.quick-functions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.function-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #f0f0f0;
}

.function-item:hover {
  background: #1e88e5;
  border-color: #1e88e5;
  transform: translateX(2px);
}

.function-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.function-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  transition: color 0.2s;
}

.function-desc {
  font-size: 12px;
  color: #999;
  transition: color 0.2s;
}

.function-item:hover .function-name,
.function-item:hover .function-desc {
  color: white;
}

.function-arrow {
  font-size: 16px;
  color: #999;
  transition: all 0.2s;
  flex-shrink: 0;
}

.function-item:hover .function-arrow {
  color: white;
  transform: translateX(4px);
}


 /* 高考倒计时样式 */
 .countdown-header {
   display: flex;
   align-items: center;
   gap: 8px;
   margin-bottom: 20px;
 }

 .countdown-content {
   display: flex;
   align-items: center;
   gap: 16px;
   margin-bottom: 20px;
 }

 .countdown-days {
   display: flex;
   align-items: baseline;
   gap: 4px;
 }

 .days-number {
   font-size: 32px;
   font-weight: 700;
   color: #ff6b6b;
   line-height: 1;
 }

 .days-label {
   font-size: 14px;
   color: #999;
   font-weight: 500;
 }

 .countdown-info {
   flex: 1;
 }

 .countdown-date {
   font-size: 12px;
   color: #666;
   margin: 0 0 4px 0;
   font-weight: 500;
 }

 .countdown-desc {
   font-size: 11px;
   color: #999;
   margin: 0;
 }

 .countdown-progress {
   margin-top: 16px;
 }

 .progress-bar {
   width: 100%;
   height: 6px;
   background: #f0f0f0;
   border-radius: 3px;
   overflow: hidden;
   margin-bottom: 8px;
 }

 .progress-fill {
   height: 100%;
   background: #ff6b6b;
   border-radius: 3px;
   transition: width 0.3s ease;
 }

 .progress-text {
   font-size: 10px;
   color: #999;
   text-align: center;
 }

 .countdown-stats {
   margin-top: auto;
   padding-top: 20px;
   border-top: 1px solid #f0f0f0;
 }

 .stat-item {
   display: flex;
   justify-content: space-between;
   align-items: center;
   margin-bottom: 10px;
 }

 .stat-label {
   font-size: 11px;
   color: #666;
 }

 .stat-value {
   font-size: 11px;
   font-weight: 600;
   color: #ff6b6b;
   background: #fff5f5;
   padding: 2px 6px;
   border-radius: 3px;
 }

 .countdown-motivation {
   margin-top: 16px;
   padding: 14px 14px 14px 10px;  /* 左内边距减少，文字向左偏移 */
   background: #fff5f5;
   border-radius: 8px;
   display: flex;
   align-items: center;
   gap: 8px;
   border: 1px solid #ff6b6b;
   border-left: 3px solid #ff6b6b;
 }

 .motivation-icon {
   font-size: 16px;
   flex-shrink: 0;
 }

 .motivation-text {
  font-size: 11px;
  color: #ff6b6b;
  font-weight: 500;
  margin: 0;
  line-height: 1.4;
  white-space: nowrap;
}

 .carousel-main {
   position: relative;
 }

.carousel {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.12);
  width: 100%;
  height: 100%;
}

.carousel-item {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.4s ease, visibility 0.4s ease;
}

.carousel-item.active {
  position: relative;
  opacity: 1;
  visibility: visible;
}

.slide-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 64px 80px;
  color: #f0f0f0;
  min-height: 380px;
  width: 100%;
  box-sizing: border-box;
  transition: background 0.4s ease;
  text-align: center;
}

.slide-text {
  max-width: 680px;
}

.slide-badge {
  display: inline-block;
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.35);
  color: #ebe8f1;
  letter-spacing: 0.5px;
}

.slide-title {
  font-size: 40px;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0,0,0,0.3);
  margin: 0 0 24px 0;
  line-height: 1.2;
  letter-spacing: -0.5px;
}

.slide-desc {
  font-size: 16px;
  color: #e8e6f3;
  line-height: 1.6;
  margin: 0 0 40px 0;
  opacity: 0.95;
  max-width: 520px;
  margin-left: auto;
  margin-right: auto;
}

.slide-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 10px;
  padding: 16px 40px;
  color: white;
  font-weight: 600;
  box-shadow: 0 6px 16px rgba(30, 136, 229, 0.4);
  transition: all 0.3s ease;
  cursor: pointer;
  font-size: 16px;
  letter-spacing: 0.5px;
}

.slide-btn:hover {
  background: rgba(255, 255, 255, 0.35);
  box-shadow: 0 10px 24px rgba(30, 136, 229, 0.6);
  transform: translateY(-4px);
}



.carousel-controls {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0 0;
}

.control-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  color: #1e88e5;
  font-size: 22px;
  border: none;
  box-shadow: 0 4px 12px rgba(102,126,234,0.25);
  transition: background 0.3s ease, transform 0.2s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover {
  background: rgba(255,255,255,0.35);
  color: #1565c0;
  transform: scale(1.1);
}

.carousel-dots {
  display: flex;
  gap: 10px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ccc;
  transition: all 0.3s ease;
  cursor: pointer;
}

.dot.active {
  background: #1976d2;
  width: 30px;
  border-radius: 8px;
}

.dot:hover {
  background: #999;
}

/* ===== 热门院校 ===== */
.schools-section {
  padding: 48px 0;
  background: white;
  margin-top: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  gap: 24px;
}

.section-title-group {
  flex: 1;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.section-subtitle {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.section-controls {
  display: flex;
  align-items: center;
  gap: 24px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  padding: 6px 14px;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab:hover,
.filter-tab.active {
  background: #1e88e5;
  color: white;
  border-color: #1e88e5;
}

.more-link {
  color: #1e88e5;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s;
  white-space: nowrap;
}

.more-link:hover {
  color: #64b5f6;
}

.schools-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.school-card {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  gap: 14px;
  align-items: center;
  width: fit-content;
  max-width: 100%;
}

.school-card:hover {
  border-color: #1e88e5;
  box-shadow: 0 6px 16px rgba(30, 136, 229, 0.15);
  transform: translateY(-3px);
}

.school-logo-wrapper {
  flex-shrink: 0;
  width: 90px;
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 10px;
  padding: 6px;
}

.school-logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 5px;
}

.school-logo-emoji {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  font-size: 45px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.school-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  padding-left: 0;
  padding-right: 0;
  width: fit-content;
  max-width: 100%;
}

.school-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

.school-location {
  font-size: 11px;
  color: #999;
  margin: 0;
  line-height: 1.2;
}

.school-tags {
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
  margin: 0;
  flex: 0 0 auto;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70vw;
}

.school-tags .tag {
  padding: 3px 7px;
  background: #f5f5f5;
  border-radius: 3px;
  font-size: 10px;
  color: #666;
  font-weight: 500;
}

.school-tags .formatted-tags {
  padding: 4px 12px;
  background: #f5f5f5;
  border-radius: 6px;
  font-size: 12px;
  color: #555;
  font-weight: 500;
  white-space: nowrap;
  margin: 0; /* 确保左右边距相等 */
}

.school-tags .tag.985 {
  background: #fce4ec;
  color: #c2185b;
}

.school-tags .tag.211 {
  background: #e3f2fd;
  color: #1565c0;
}

.school-footer {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 8px;
  padding-top: 6px;
  margin-top: 4px;
  border-top: 1px solid #f0f0f0;
  width: fit-content;
  max-width: 100%;
}


.type-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.view-link {
  font-size: 12px;
  color: #1e88e5;
  font-weight: 500;
  transition: color 0.2s;
  white-space: nowrap;
}

.school-card:hover .view-link {
  color: #64b5f6;
}

/* ===== 热门专业 ===== */
.majors-section {
  padding: 48px 0;
  background: #fafbfc;
  margin-top: 16px;
}

.majors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
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
  background: #f8fafc;
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
}

.major-meta {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta-label {
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
}

.meta-value {
  color: #1a1a1a;
  font-weight: 600;
  font-size: 0.95rem;
}

.major-stat .value {
  display: block;
  font-size: 14px;
  font-weight: 700;
  background: #f093fb;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}


/* ===== 用户评价 ===== */
.testimonial-section {
  padding: 48px 0;
  background: #fafbfc;
  margin-top: 16px;
}

.testimonial-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.testimonial-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e8e8e8;
  transition: all 0.2s;
}

.testimonial-card:hover {
  border-color: #1e88e5;
  box-shadow: 0 8px 24px rgba(30, 136, 229, 0.1);
  transform: translateY(-4px);
}

.testimonial-header {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.testimonial-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #1e88e5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.testimonial-info {
  flex: 1;
}

.testimonial-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 2px 0;
}

.testimonial-role {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.testimonial-rating {
  margin-bottom: 12px;
}

.star {
  color: #ffc107;
  font-size: 14px;
  margin-right: 2px;
}

.testimonial-content {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* ===== 常见问题 ===== */
.faq-section {
  padding: 48px 0;
  background: white;
  margin-top: 16px;
}

.faq-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 16px;
}

.faq-item {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}

.faq-item:hover {
  border-color: #1e88e5;
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.1);
}

.faq-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  background: #f8f9fa;
  transition: background 0.2s;
}

.faq-item:hover .faq-header {
  background: #f0f2f5;
}

.faq-question {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  flex: 1;
}

.faq-toggle {
  font-size: 20px;
  color: #1e88e5;
  font-weight: 300;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.faq-toggle.active {
  transform: rotate(45deg);
}

.faq-answer {
  padding: 16px;
  background: white;
  border-top: 1px solid #e8e8e8;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 500px;
  }
}

.faq-answer p {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* ===== CTA 区域 ===== */
.cta-section {
  padding: 60px 0;
  background: #1e88e5;
  margin-top: 40px;
  position: relative;
  overflow: hidden;
}

.cta-section::before {
  content: '';
  position: absolute;
  top: -40%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
}

.cta-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.cta-title {
  font-size: 40px;
  font-weight: 700;
  color: white;
  margin: 0 0 12px 0;
}

.cta-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 28px 0;
}

.cta-btn {
  padding: 14px 40px;
  background: white;
  color: #1e88e5;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.cta-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

/* ===== 底部 ===== */
.footer {
  background: #1a1a1a;
  color: #999;
  padding: 48px 0 20px;
  margin-top: 40px;
}

.footer-content {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
}

.footer-col-centered {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 600px;
}

.footer-title {
  color: white;
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 16px 0;
}

.footer-desc {
  font-size: 14px;
  line-height: 1.8;
  margin: 0;
  color: #e0e0e0;
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #333;
}

.footer-copyright {
  font-size: 12px;
  color: #666;
  margin: 0;
}

.footer-copyright a {
  color: #999;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-copyright a:hover {
  color: white;
}

/* ===== 回到顶部 ===== */
.back-to-top {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 44px;
  height: 44px;
  background: #1e88e5;
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 18px;
  cursor: pointer;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
  font-weight: 600;
}

.back-to-top.visible {
  opacity: 1;
  visibility: visible;
}

.back-to-top:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(30, 136, 229, 0.4);
}

/* ===== 响应式设计 ===== */
@media (max-width: 1024px) {
  .hero-title {
    font-size: 36px;
  }

  .slide-content {
    padding: 40px 32px;
    min-height: 280px;
  }

  .slide-title {
    font-size: 32px;
  }

  .slide-image {
    font-size: 100px;
  }

  .trend-content {
    grid-template-columns: 1fr;
  }

  .news-container {
    grid-template-columns: 1fr;
  }

  .news-list {
    grid-column: auto;
  }

  .faq-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .section-controls {
    width: 100%;
    justify-content: space-between;
  }
}

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
    padding: 40px 0;
  }

  .hero-title {
    font-size: 28px;
  }

  .hero-subtitle {
    font-size: 15px;
    margin-bottom: 20px;
  }

  .search-container {
    flex-direction: column;
  }

  .search-btn {
    width: 100%;
  }

  .quick-nav-row {
    flex-wrap: wrap;
    gap: 8px;
  }

  .quick-nav-item {
    flex: 1 1 calc(50% - 8px);
    min-width: 140px;
  }

  .quick-nav-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-number {
    font-size: 28px;
  }

  .slide-content {
    flex-direction: column;
    padding: 32px 24px;
    min-height: 240px;
  }

  .slide-title {
    font-size: 24px;
  }

  .slide-desc {
    font-size: 14px;
  }

  .slide-image {
    font-size: 80px;
    margin-top: 16px;
  }

  .schools-grid,
  .majors-grid,
  .guide-grid,
  .testimonial-grid {
    grid-template-columns: 1fr;
  }

  .section-title {
    font-size: 22px;
  }

  .cta-title {
    font-size: 28px;
  }

  .footer-content {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 12px;
  }

  .header .container {
    padding: 8px 12px;
  }

  .logo-text {
    font-size: 15px;
  }

  .nav {
    gap: 12px;
    font-size: 13px;
  }

  .search-mini {
    display: none;
  }

  .btn {
    padding: 7px 13px;
    font-size: 13px;
  }

  .hero-section {
    padding: 24px 0;
  }

  .hero-title {
    font-size: 22px;
  }

  .hero-subtitle {
    font-size: 13px;
    margin-bottom: 16px;
  }

  .search-input {
    padding: 10px 12px;
    font-size: 13px;
  }

  .search-btn {
    padding: 10px 16px;
    font-size: 13px;
  }

  .suggestion-tag {
    font-size: 12px;
    padding: 3px 10px;
  }

  .quick-nav-row {
    flex-direction: column;
    gap: 8px;
  }

  .quick-nav-item {
    flex: 1 1 auto;
    min-width: auto;
  }

  .quick-nav-grid {
    grid-template-columns: 1fr;
  }

  .nav-item-title {
    font-size: 14px;
  }

  .nav-item-desc {
    font-size: 11px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-number {
    font-size: 24px;
  }

  .stat-label {
    font-size: 14px;
  }

  .carousel-section {
    padding: 16px 0;
  }

  .carousel-layout {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .side-module {
    order: 2;
    min-height: auto;
  }

  .carousel-main {
    order: 1;
  }

  .carousel-item {
    position: relative;
  }

  .module-card {
    padding: 16px;
    min-height: auto;
  }

  .module-icon {
    font-size: 24px;
  }

  .module-title {
    font-size: 14px;
  }

  .module-desc {
    font-size: 11px;
  }

  .stat-value {
    font-size: 12px;
  }

  .hot-text {
    font-size: 11px;
  }

  .slide-content {
    padding: 24px 16px;
    min-height: 200px;
  }

  .slide-badge {
    font-size: 11px;
    padding: 4px 10px;
    margin-bottom: 12px;
  }

  .slide-title {
    font-size: 18px;
    margin-bottom: 8px;
  }

  .slide-desc {
    font-size: 12px;
    margin-bottom: 12px;
  }

  .slide-btn {
    padding: 8px 20px;
    font-size: 12px;
  }

  .slide-image {
    font-size: 60px;
    margin-top: 12px;
  }

  .carousel-controls {
    gap: 12px;
    padding: 12px 0;
  }

  .control-btn {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }

  .dot {
    width: 6px;
    height: 6px;
  }

  .dot.active {
    width: 18px;
  }

  .schools-section,
  .majors-section,
  .trend-section,
  .guide-section,
  .news-section,
  .testimonial-section,
  .faq-section {
    padding: 32px 0;
  }

  .section-title {
    font-size: 18px;
  }

  .section-subtitle {
    font-size: 12px;
  }

  .section-header {
    margin-bottom: 20px;
  }

  .filter-tabs {
    gap: 6px;
  }

  .filter-tab {
    padding: 4px 10px;
    font-size: 12px;
  }

  .more-link {
    font-size: 12px;
  }

  .school-card,
  .major-card,
  .guide-card,
  .testimonial-card {
    padding: 16px;
  }

  .school-rank {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }

  .school-header {
    gap: 10px;
    margin-bottom: 12px;
  }

  .school-logo {
    width: 55px;
    height: 55px;
    font-size: 28px;
  }

  .school-name {
    font-size: 14px;
  }

  .school-location {
    font-size: 11px;
  }

  .school-stats {
    gap: 12px;
    padding: 8px 0;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 14px;
  }

  .stat-name {
    font-size: 10px;
  }

  .action-btn {
    padding: 6px 10px;
    font-size: 11px;
  }

  .major-icon {
    font-size: 32px;
  }

  .major-badge {
    padding: 3px 8px;
    font-size: 10px;
  }

  .major-name {
    font-size: 14px;
    margin-bottom: 6px;
  }

  .major-desc {
    font-size: 12px;
    margin-bottom: 12px;
  }

  .major-stats {
    gap: 12px;
    padding-top: 12px;
  }

  .major-stat .label {
    font-size: 10px;
  }

  .major-stat .value {
    font-size: 13px;
  }

  .trend-chart {
    padding: 20px;
  }

  .chart-bars {
    height: 150px;
    gap: 8px;
  }

  .chart-labels {
    font-size: 11px;
  }

  .trend-insights {
    gap: 12px;
  }

  .insights-title {
    font-size: 16px;
    margin-bottom: 4px;
  }

  .insight-item {
    padding: 12px;
    gap: 10px;
  }

  .insight-icon {
    font-size: 20px;
  }

  .insight-content .insight-title {
    font-size: 13px;
  }

  .insight-content .insight-desc {
    font-size: 11px;
  }

  .guide-number {
    font-size: 28px;
  }

  .guide-title {
    font-size: 16px;
  }

  .guide-desc {
    font-size: 12px;
  }

  .featured-item {
    padding: 20px;
    min-height: 240px;
  }

  .featured-image {
    font-size: 48px;
    margin-bottom: 12px;
  }

  .featured-title {
    font-size: 16px;
    margin-bottom: 8px;
  }

  .featured-desc {
    font-size: 12px;
    margin-bottom: 12px;
  }

  .news-item {
    padding: 12px;
  }

  .news-item-title {
    font-size: 13px;
  }

  .news-item-tag {
    font-size: 10px;
    padding: 2px 6px;
  }

  .news-item-desc {
    font-size: 11px;
    margin-bottom: 6px;
  }

  .news-item-meta {
    font-size: 10px;
  }

  .testimonial-avatar {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }

  .testimonial-name {
    font-size: 13px;
  }

  .testimonial-role {
    font-size: 11px;
  }

  .testimonial-content {
    font-size: 12px;
  }

  .faq-header {
    padding: 12px;
  }

  .faq-question {
    font-size: 13px;
  }

  .faq-answer {
    padding: 12px;
  }

  .faq-answer p {
    font-size: 12px;
  }

  .cta-section {
    padding: 40px 0;
  }

  .cta-title {
    font-size: 22px;
    margin-bottom: 8px;
  }

  .cta-subtitle {
    font-size: 13px;
    margin-bottom: 20px;
  }

  .cta-btn {
    padding: 10px 28px;
    font-size: 13px;
  }

  .footer {
    padding: 32px 0 12px;
  }

  .footer-content {
    gap: 20px;
    margin-bottom: 20px;
  }

  .footer-copyright {
    font-size: 11px;
  }

  .back-to-top {
    width: 40px;
    height: 40px;
    font-size: 16px;
    bottom: 16px;
    right: 16px;
  }
}
</style>