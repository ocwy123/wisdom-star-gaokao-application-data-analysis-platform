<template>
  <div class="dashboard">
    <!-- 加载动画 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <p class="loading-text">数据加载中...</p>
      </div>
    </div>

    <!-- 顶部导航 -->
    <header class="header" :class="{ scrolled: isScrolled }">
      <div class="container">
        <div class="logo" @click="scrollToTop">
          <span class="logo-icon">🎓</span>
          <span class="logo-text">高考志愿分析平台</span>
        </div>
        <nav class="nav">
          <router-link 
            to="/" 
            class="nav-item" 
            :class="{ active: $route.path === '/' }"
            @click="scrollToTop"
          >
            首页
          </router-link>
          <router-link to="/schools" class="nav-item">高校查询</router-link>
          <router-link to="#" class="nav-item">专业查询</router-link>
          <router-link to="#" class="nav-item">志愿填报</router-link>
          <router-link to="#" class="nav-item">政策资讯</router-link>
        </nav>
        <div class="user-actions">
          <button class="btn btn-primary" @click="showLoginModal">
            <span class="btn-icon">👤</span>
            登录/注册
          </button>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main">
      <!-- 搜索区域 -->
      <section class="hero">
        <div class="hero-bg">
          <div class="bg-particle"></div>
          <div class="bg-particle"></div>
          <div class="bg-particle"></div>
        </div>
        <div class="container">
          <div class="hero-content" :class="{ animated: !loading }">
            <h1 class="hero-title">
              <span class="title-line">高考志愿智能分析</span>
              <span class="title-line highlight">平台</span>
            </h1>
            <p class="hero-subtitle">基于大数据分析，为您的志愿填报提供科学决策支持</p>
            <div class="search-box">
              <div class="search-container">
                <input 
                  type="text" 
                  placeholder="搜索高校、专业或政策资讯..." 
                  class="search-input"
                  v-model="searchQuery"
                  @focus="onSearchFocus"
                  @blur="onSearchBlur"
                >
                <button class="search-btn" @click="handleSearch">
                  <span class="search-icon">🔍</span>
                  搜索
                </button>
              </div>
            </div>
            <div class="quick-tags">
              <span class="tag-label">热门搜索：</span>
              <a 
                v-for="tag in hotTags" 
                :key="tag" 
                href="#" 
                class="tag"
                @click="quickSearch(tag)"
              >
                {{ tag }}
              </a>
            </div>
          </div>
        </div>
      </section>

      <!-- 数据概览 -->
      <section class="stats-section">
        <div class="container">
          <div class="section-header" :class="{ animated: !loading }">
            <h2 class="section-title">数据概览</h2>
            <p class="section-desc">实时掌握高考数据动态，助力科学志愿填报</p>
          </div>
          <div class="stats-grid">
            <div 
              class="stat-card" 
              v-for="(stat, index) in statistics" 
              :key="stat.label"
              :style="{ animationDelay: `${index * 0.1}s` }"
              :class="{ animated: !loading }"
            >
              <div class="stat-icon" :style="{ background: stat.color }">
                <span class="icon">{{ stat.icon }}</span>
                <div class="icon-glow"></div>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
              <div class="stat-trend" :class="stat.trend">
                <span class="trend-icon">{{ stat.trendIcon }}</span>
                <span class="trend-text">{{ stat.change }}</span>
              </div>
              <div class="card-glow"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- 热门院校推荐 -->
      <section class="recommend-section">
        <div class="container">
          <div class="section-header" :class="{ animated: !loading }">
            <h2 class="section-title">热门院校推荐</h2>
            <p class="section-desc">根据历年录取数据和考生偏好，为您推荐优质院校</p>
          </div>
          <div class="recommend-grid">
            <div 
              class="school-card" 
              v-for="(school, index) in recommendedSchools" 
              :key="school.id"
              :style="{ animationDelay: `${index * 0.1}s` }"
              :class="{ animated: !loading }"
              @click="viewSchoolDetail(school.id)"
            >
              <div class="school-badge" :class="getSchoolBadge(school.level)">
                {{ school.level }}
              </div>
              <div class="school-logo">
                <span class="logo">{{ school.logo }}</span>
              </div>
              <div class="school-info">
                <h3 class="school-name">{{ school.name }}</h3>
                <p class="school-location">📍 {{ school.location }}</p>
                <div class="school-tags">
                  <span class="tag" v-for="tag in school.tags" :key="tag">{{ tag }}</span>
                </div>
                <div class="school-stats">
                  <div class="stat">
                    <span class="value">{{ school.avgScore }}</span>
                    <span class="label">平均分</span>
                  </div>
                  <div class="stat">
                    <span class="value">{{ school.rank }}</span>
                    <span class="label">排名</span>
                  </div>
                  <div class="stat">
                    <span class="value">{{ school.employmentRate }}</span>
                    <span class="label">就业率</span>
                  </div>
                </div>
              </div>
              <div class="school-hover">
                <span>查看详情 →</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 图表区域 -->
      <section class="charts-section">
        <div class="container">
          <div class="charts-grid">
            <!-- 热度排行 -->
            <div 
              class="chart-card" 
              :class="{ animated: !loading }"
            >
              <div class="chart-header">
                <h3 class="chart-title">
                  <span class="chart-icon">🏫</span>
                  高校热度排行
                </h3>
                <button class="btn-more" @click="navigateToSchools">
                  查看更多
                  <span class="btn-arrow">→</span>
                </button>
              </div>
              <div class="rank-list" v-if="schoolRank.length">
                <div 
                  class="rank-item" 
                  v-for="(item, index) in schoolRank" 
                  :key="item.school_id"
                  @click="viewSchoolDetail(item.school_id)"
                >
                  <div class="rank-info">
                    <span class="rank-number" :class="getRankClass(index)">
                      {{ index + 1 }}
                    </span>
                    <span class="rank-name">{{ item.school_name }}</span>
                  </div>
                  <div class="rank-score">
                    <span class="score">{{ item.heat_score }}</span>
                    <span class="score-label">热度</span>
                  </div>
                  <div class="rank-hover">查看详情 →</div>
                </div>
              </div>
              <div class="empty" v-else>
                <div class="empty-content">
                  <span class="empty-icon">📊</span>
                  <span class="empty-text">暂无数据</span>
                </div>
              </div>
            </div>

            <!-- 专业排行 -->
            <div 
              class="chart-card" 
              :class="{ animated: !loading }"
            >
              <div class="chart-header">
                <h3 class="chart-title">
                  <span class="chart-icon">📚</span>
                  专业热度排行
                </h3>
                <button class="btn-more" @click="navigateToMajors">
                  查看更多
                  <span class="btn-arrow">→</span>
                </button>
              </div>
              <div class="rank-list" v-if="majorRank.length">
                <div 
                  class="rank-item" 
                  v-for="(item, index) in majorRank" 
                  :key="item.major_id"
                  @click="viewMajorDetail(item.major_id)"
                >
                  <div class="rank-info">
                    <span class="rank-number" :class="getRankClass(index)">
                      {{ index + 1 }}
                    </span>
                    <span class="rank-name">{{ item.major_name }}</span>
                  </div>
                  <div class="rank-score">
                    <span class="score">{{ item.heat_score }}</span>
                    <span class="score-label">热度</span>
                  </div>
                  <div class="rank-hover">查看详情 →</div>
                </div>
              </div>
              <div class="empty" v-else>
                <div class="empty-content">
                  <span class="empty-icon">📊</span>
                  <span class="empty-text">暂无数据</span>
                </div>
              </div>
            </div>

            <!-- 分数线趋势 -->
            <div 
              class="chart-card full-width" 
              :class="{ animated: !loading }"
            >
              <div class="chart-header">
                <h3 class="chart-title">
                  <span class="chart-icon">📈</span>
                  历年分数线趋势
                </h3>
                <div class="chart-controls">
                  <select class="filter-select" v-model="selectedProvince">
                    <option value="">全国</option>
                    <option value="北京">北京</option>
                    <option value="上海">上海</option>
                    <option value="广东">广东</option>
                    <option value="江苏">江苏</option>
                  </select>
                  <select class="filter-select" v-model="selectedBatch">
                    <option value="">全部批次</option>
                    <option value="本科一批">本科一批</option>
                    <option value="本科二批">本科二批</option>
                    <option value="专科批">专科批</option>
                  </select>
                </div>
              </div>
              <div class="chart-container">
                <div ref="scoreTrendChart" class="chart"></div>
              </div>
            </div>

            <!-- 各省难度 -->
            <div 
              class="chart-card" 
              :class="{ animated: !loading }"
            >
              <div class="chart-header">
                <h3 class="chart-title">
                  <span class="chart-icon">🗺️</span>
                  各省录取难度
                </h3>
              </div>
              <div class="chart-container">
                <div ref="provinceChart" class="chart"></div>
              </div>
            </div>

            <!-- 招生计划 -->
            <div 
              class="chart-card" 
              :class="{ animated: !loading }"
            >
              <div class="chart-header">
                <h3 class="chart-title">
                  <span class="chart-icon">📊</span>
                  招生计划分布
                </h3>
              </div>
              <div class="chart-container">
                <div ref="planChart" class="chart"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 新闻资讯 -->
      <section class="news-section">
        <div class="container">
          <div class="section-header" :class="{ animated: !loading }">
            <h2 class="section-title">最新资讯</h2>
            <p class="section-desc">及时了解高考政策变化和招生动态</p>
          </div>
          <div class="news-grid">
            <div 
              class="news-card" 
              v-for="(news, index) in newsList" 
              :key="news.id"
              :style="{ animationDelay: `${index * 0.1}s` }"
              :class="{ animated: !loading }"
              @click="viewNewsDetail(news.id)"
            >
              <div class="news-image">
                <span class="image-icon">{{ news.icon }}</span>
              </div>
              <div class="news-content">
                <div class="news-meta">
                  <span class="news-category" :class="news.category">{{ news.category }}</span>
                  <span class="news-date">{{ news.date }}</span>
                </div>
                <h3 class="news-title">{{ news.title }}</h3>
                <p class="news-desc">{{ news.description }}</p>
                <div class="news-footer">
                  <span class="news-source">{{ news.source }}</span>
                  <span class="news-read">{{ news.readCount }} 阅读</span>
                </div>
              </div>
              <div class="news-hover">
                <span>阅读全文 →</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 备考指南 -->
      <section class="guide-section">
        <div class="container">
          <div class="section-header" :class="{ animated: !loading }">
            <h2 class="section-title">备考指南</h2>
            <p class="section-desc">科学备考策略，助力高考冲刺</p>
          </div>
          <div class="guide-grid">
            <div 
              class="guide-card" 
              v-for="(guide, index) in guideList" 
              :key="guide.id"
              :style="{ animationDelay: `${index * 0.1}s` }"
              :class="{ animated: !loading }"
              @click="viewGuideDetail(guide.id)"
            >
              <div class="guide-icon">
                <span class="icon">{{ guide.icon }}</span>
              </div>
              <h3 class="guide-title">{{ guide.title }}</h3>
              <p class="guide-desc">{{ guide.description }}</p>
              <div class="guide-tags">
                <span class="tag" v-for="tag in guide.tags" :key="tag">{{ tag }}</span>
              </div>
              <div class="guide-hover">
                <span>查看详情 →</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 政策解读 -->
      <section class="policy-section">
        <div class="container">
          <div class="section-header" :class="{ animated: !loading }">
            <h2 class="section-title">政策解读</h2>
            <p class="section-desc">深度解析高考政策，把握填报机会</p>
          </div>
          <div class="policy-grid">
            <div 
              class="policy-card" 
              v-for="(policy, index) in policyList" 
              :key="policy.id"
              :style="{ animationDelay: `${index * 0.1}s` }"
              :class="{ animated: !loading }"
              @click="viewPolicyDetail(policy.id)"
            >
              <div class="policy-header">
                <h3 class="policy-title">{{ policy.title }}</h3>
                <span class="policy-date">{{ policy.date }}</span>
              </div>
              <p class="policy-summary">{{ policy.summary }}</p>
              <div class="policy-tags">
                <span class="tag" v-for="tag in policy.tags" :key="tag">{{ tag }}</span>
              </div>
              <div class="policy-footer">
                <span class="policy-author">发布：{{ policy.author }}</span>
                <span class="policy-views">{{ policy.views }} 浏览</span>
              </div>
              <div class="policy-hover">
                <span>查看详情 →</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 用户评价 -->
      <section class="testimonials-section">
        <div class="container">
          <div class="section-header" :class="{ animated: !loading }">
            <h2 class="section-title">用户评价</h2>
            <p class="section-desc">听听其他考生和家长的真实反馈</p>
          </div>
          <div class="testimonials-grid">
            <div 
              class="testimonial-card" 
              v-for="(testimonial, index) in testimonials" 
              :key="testimonial.id"
              :style="{ animationDelay: `${index * 0.1}s` }"
              :class="{ animated: !loading }"
            >
              <div class="testimonial-header">
                <div class="user-avatar">
                  <span class="avatar">{{ testimonial.avatar }}</span>
                </div>
                <div class="user-info">
                  <h4 class="user-name">{{ testimonial.name }}</h4>
                  <p class="user-desc">{{ testimonial.desc }}</p>
                </div>
                <div class="rating">
                  <span class="stars">{{ testimonial.rating }}</span>
                </div>
              </div>
              <p class="testimonial-content">{{ testimonial.content }}</p>
              <div class="testimonial-footer">
                <span class="testimonial-date">{{ testimonial.date }}</span>
                <span class="testimonial-school">{{ testimonial.school }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 功能入口 -->
      <section class="features-section">
        <div class="container">
          <div class="section-header" :class="{ animated: !loading }">
            <h2 class="section-title">核心功能</h2>
            <p class="section-desc">一站式高考志愿填报服务</p>
          </div>
          <div class="features-grid">
            <div 
              class="feature-card" 
              v-for="(feature, index) in features" 
              :key="feature.title"
              :style="{ animationDelay: `${index * 0.1}s` }"
              :class="{ animated: !loading }"
              @click="navigateToFeature(feature.route)"
            >
              <div class="feature-icon">
                <span class="icon">{{ feature.icon }}</span>
                <div class="icon-glow"></div>
              </div>
              <h4 class="feature-title">{{ feature.title }}</h4>
              <p class="feature-desc">{{ feature.desc }}</p>
              <div class="feature-hover">
                <span>立即体验 →</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 底部 -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <h4>关于我们</h4>
            <p>致力于为高考考生提供最专业、最全面的志愿填报服务</p>
          </div>
          <div class="footer-section">
            <h4>联系方式</h4>
            <p>客服热线：400-123-4567</p>
            <p>邮箱：service@gkzy.com</p>
          </div>
          <div class="footer-section">
            <h4>关注我们</h4>
            <div class="social-links">
              <a href="#" class="social-link">微信</a>
              <a href="#" class="social-link">微博</a>
              <a href="#" class="social-link">QQ群</a>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>© 2026 高考志愿数据分析平台 版权所有</p>
        </div>
      </div>
    </footer>

    <!-- 回到顶部按钮 -->
    <button 
      class="back-to-top" 
      :class="{ visible: showBackToTop }"
      @click="scrollToTop"
    >
      <span class="arrow">↑</span>
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  getStatistics,
  getSchoolRank,
  getMajorRank,
  getScoreTrend,
  getProvinceDifficulty,
  getPlanDistribution
} from '../api/overview'

const router = useRouter()

const loading = ref(true)
const isScrolled = ref(false)
const showBackToTop = ref(false)
const searchQuery = ref('')
const selectedProvince = ref('')
const selectedBatch = ref('')

const statistics = ref([])
const schoolRank = ref([])
const majorRank = ref([])
const scoreTrendChart = ref(null)
const provinceChart = ref(null)
const planChart = ref(null)

const hotTags = ['清华大学', '计算机科学与技术', '985高校', '北京', '临床医学']

const statCards = [
  { 
    label: '高校总数', 
    icon: '🏫', 
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    trend: 'up',
    trendIcon: '↗',
    change: '+5.2%'
  },
  { 
    label: '专业总数', 
    icon: '📚', 
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    trend: 'up',
    trendIcon: '↗',
    change: '+3.8%'
  },
  { 
    label: '录取数据量', 
    icon: '📊', 
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    trend: 'up',
    trendIcon: '↗',
    change: '+12.5%'
  },
  { 
    label: '覆盖省份', 
    icon: '🗺️', 
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    trend: 'stable',
    trendIcon: '→',
    change: '0%'
  }
]

const recommendedSchools = [
  {
    id: 1,
    name: '清华大学',
    location: '北京',
    level: '985',
    logo: '🏛️',
    tags: ['顶尖', '理工', '综合'],
    avgScore: '680',
    rank: '1',
    employmentRate: '98%'
  },
  {
    id: 2,
    name: '北京大学',
    location: '北京',
    level: '985',
    logo: '🎓',
    tags: ['顶尖', '文科', '综合'],
    avgScore: '675',
    rank: '2',
    employmentRate: '97%'
  },
  {
    id: 3,
    name: '复旦大学',
    location: '上海',
    level: '985',
    logo: '📚',
    tags: ['顶尖', '综合', '医学'],
    avgScore: '670',
    rank: '3',
    employmentRate: '96%'
  },
  {
    id: 4,
    name: '上海交通大学',
    location: '上海',
    level: '985',
    logo: '⚓',
    tags: ['理工', '工程', '创新'],
    avgScore: '668',
    rank: '4',
    employmentRate: '95%'
  }
]

const newsList = [
  {
    id: 1,
    title: '2026年高考政策重大调整，这些变化考生需注意',
    description: '教育部发布最新高考政策，涉及考试科目、录取方式等多个方面...',
    category: '政策',
    date: '2026-03-15',
    source: '教育部',
    readCount: '2.5万',
    icon: '📰'
  },
  {
    id: 2,
    title: '985高校新增专业名单公布，人工智能成热门',
    description: '多所985高校新增人工智能、大数据等前沿专业，为考生提供更多选择...',
    category: '招生',
    date: '2026-03-14',
    source: '高校招生网',
    readCount: '1.8万',
    icon: '🎯'
  },
  {
    id: 3,
    title: '高考志愿填报时间确定，这些时间节点要牢记',
    description: '各省市高考志愿填报时间陆续公布，考生需提前做好准备...',
    category: '填报',
    date: '2026-03-13',
    source: '教育在线',
    readCount: '1.2万',
    icon: '⏰'
  },
  {
    id: 4,
    title: '名校录取分数线预测分析，你的分数能上哪所大学',
    description: '基于历年数据，预测2026年各高校录取分数线，为考生提供参考...',
    category: '分析',
    date: '2026-03-12',
    source: '数据分析',
    readCount: '9800',
    icon: '📊'
  }
]

const guideList = [
  {
    id: 1,
    title: '高考冲刺阶段复习策略',
    description: '最后三个月如何高效复习，提升成绩的关键技巧',
    icon: '🚀',
    tags: ['复习', '策略', '提分']
  },
  {
    id: 2,
    title: '志愿填报常见问题解答',
    description: '解答考生和家长在志愿填报过程中遇到的各类问题',
    icon: '❓',
    tags: ['填报', '问答', '技巧']
  },
  {
    id: 3,
    title: '心理调节与压力管理',
    description: '高考期间如何保持良好心态，应对考试压力',
    icon: '🧠',
    tags: ['心理', '调节', '压力']
  },
  {
    id: 4,
    title: '各科备考重点与难点',
    description: '分析各科目备考重点，攻克难点知识点',
    icon: '📝',
    tags: ['备考', '重点', '难点']
  }
]

const policyList = [
  {
    id: 1,
    title: '新高考改革政策深度解读',
    summary: '全面解析新高考改革政策对考生志愿填报的影响',
    date: '2026-03-10',
    author: '政策研究室',
    views: '3.2万',
    tags: ['改革', '政策', '解读']
  },
  {
    id: 2,
    title: '特殊类型招生政策分析',
    summary: '艺术、体育、保送等特殊类型招生政策详解',
    date: '2026-03-09',
    author: '招生办',
    views: '2.1万',
    tags: ['特殊招生', '政策', '分析']
  },
  {
    id: 3,
    title: '平行志愿填报策略指南',
    summary: '如何科学合理地填报平行志愿，提高录取概率',
    date: '2026-03-08',
    author: '志愿专家',
    views: '1.8万',
    tags: ['平行志愿', '策略', '指南']
  }
]

const testimonials = [
  {
    id: 1,
    name: '张同学',
    desc: '2025年考生',
    avatar: '👦',
    content: '这个平台帮我找到了最适合的学校和专业，最终被心仪的大学录取！',
    rating: '⭐⭐⭐⭐⭐',
    date: '2025-08-15',
    school: '清华大学'
  },
  {
    id: 2,
    name: '李家长',
    desc: '考生家长',
    avatar: '👩',
    content: '数据分析很准确，志愿推荐很科学，让孩子少走了很多弯路。',
    rating: '⭐⭐⭐⭐⭐',
    date: '2025-08-10',
    school: '北京大学'
  },
  {
    id: 3,
    name: '王老师',
    desc: '高中教师',
    avatar: '👨‍🏫',
    content: '作为老师，我推荐所有考生使用这个平台，数据权威，分析专业。',
    rating: '⭐⭐⭐⭐⭐',
    date: '2025-08-05',
    school: '复旦大学'
  }
]

const features = [
  {
    icon: '🔍',
    title: '智能搜索',
    desc: '快速查找高校、专业信息',
    route: '/search'
  },
  {
    icon: '📊',
    title: '数据分析',
    desc: '历年数据深度分析对比',
    route: '/analysis'
  },
  {
    icon: '🎯',
    title: '志愿推荐',
    desc: '基于成绩智能推荐院校',
    route: '/recommend'
  },
  {
    icon: '📈',
    title: '趋势预测',
    desc: '录取趋势科学预测分析',
    route: '/trend'
  }
]

onMounted(async () => {
  setupScrollListener()
  await loadAllData()
  setTimeout(() => {
    loading.value = false
  }, 1000)
})

onUnmounted(() => {
  removeScrollListener()
})

function setupScrollListener() {
  window.addEventListener('scroll', handleScroll)
}

function removeScrollListener() {
  window.removeEventListener('scroll', handleScroll)
}

function handleScroll() {
  isScrolled.value = window.scrollY > 50
  showBackToTop.value = window.scrollY > 300
}

async function loadAllData() {
  try {
    await Promise.all([
      loadStatistics(),
      loadSchoolRank(),
      loadMajorRank(),
      loadScoreTrend(),
      loadProvinceDifficulty(),
      loadPlanDistribution()
    ])
  } catch (error) {
    console.error('数据加载失败', error)
  }
}

function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

function onSearchFocus() {
  // 搜索框聚焦效果
}

function onSearchBlur() {
  // 搜索框失焦效果
}

function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchQuery.value)}`)
  }
}

function quickSearch(tag) {
  searchQuery.value = tag
  handleSearch()
}

function showLoginModal() {
  // 显示登录模态框
  console.log('显示登录模态框')
}

function navigateToSchools() {
  router.push('/schools')
}

function navigateToMajors() {
  router.push('/majors')
}

function viewSchoolDetail(schoolId) {
  router.push(`/schools/${schoolId}`)
}

function viewMajorDetail(majorId) {
  router.push(`/majors/${majorId}`)
}

function viewNewsDetail(newsId) {
  router.push(`/news/${newsId}`)
}

function viewGuideDetail(guideId) {
  router.push(`/guide/${guideId}`)
}

function viewPolicyDetail(policyId) {
  router.push(`/policy/${policyId}`)
}

function navigateToFeature(route) {
  router.push(route)
}

function getRankClass(index) {
  if (index === 0) return 'rank-1'
  if (index === 1) return 'rank-2'
  if (index === 2) return 'rank-3'
  return 'rank-other'
}

function getSchoolBadge(level) {
  if (level === '985') return 'badge-985'
  if (level === '211') return 'badge-211'
  return 'badge-other'
}

async function loadStatistics() {
  try {
    const res = await getStatistics()
    const data = res.data
    statistics.value = statCards.map(card => ({
      ...card,
      value: formatValue(card.label, data)
    }))
  } catch (error) {
    console.error('加载统计数据失败', error)
    statistics.value = statCards.map(card => ({
      ...card,
      value: '***'
    }))
  }
}

function formatValue(label, data) {
  const map = {
    '高校总数': data.school_count,
    '专业总数': data.major_count,
    '录取数据量': data.record_count,
    '覆盖省份': data.province_count
  }
  const value = map[label]
  return value && value > 0 ? value : '***'
}

async function loadSchoolRank() {
  try {
    const res = await getSchoolRank({ limit: 10 })
    schoolRank.value = res.data && res.data.length > 0 ? res.data : []
  } catch (error) {
    console.error('加载高校排行失败', error)
    schoolRank.value = []
  }
}

async function loadMajorRank() {
  try {
    const res = await getMajorRank({ limit: 10 })
    majorRank.value = res.data && res.data.length > 0 ? res.data : []
  } catch (error) {
    console.error('加载专业排行失败', error)
    majorRank.value = []
  }
}

async function loadScoreTrend() {
  try {
    const res = await getScoreTrend({ 
      province: selectedProvince.value,
      batch: selectedBatch.value,
      years: 5 
    })
    const data = res.data && res.data.length > 0 ? res.data : []
    renderScoreTrendChart(data)
  } catch (error) {
    console.error('加载分数线趋势失败', error)
    renderScoreTrendChart([])
  }
}

function renderScoreTrendChart(data) {
  if (!scoreTrendChart.value) return
  
  const chart = echarts.init(scoreTrendChart.value)
  
  if (!data || data.length === 0) {
    chart.setOption({
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 16,
          fontWeight: 'normal'
        }
      }
    })
    return
  }
  
  const years = data.map(item => item.year).reverse()
  
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { 
      data: ['平均分', '最低分', '最高分'],
      textStyle: { color: '#666' }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: years,
      axisLine: { lineStyle: { color: '#ddd' } },
      axisLabel: { color: '#666' }
    },
    yAxis: { 
      type: 'value', 
      name: '分数',
      axisLine: { lineStyle: { color: '#ddd' } },
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#f0f0f0' } }
    },
    series: [
      {
        name: '平均分',
        type: 'line',
        data: data.map(item => item.avg_score).reverse(),
        smooth: true,
        lineStyle: { width: 3 },
        itemStyle: { color: '#3498db' }
      },
      {
        name: '最低分',
        type: 'line',
        data: data.map(item => item.min_score).reverse(),
        smooth: true,
        lineStyle: { width: 2 },
        itemStyle: { color: '#2ecc71' }
      },
      {
        name: '最高分',
        type: 'line',
        data: data.map(item => item.max_score).reverse(),
        smooth: true,
        lineStyle: { width: 2 },
        itemStyle: { color: '#e74c3c' }
      }
    ]
  })
}

async function loadProvinceDifficulty() {
  try {
    const res = await getProvinceDifficulty()
    const data = res.data && res.data.length > 0 ? res.data.slice(0, 10) : []
    renderProvinceChart(data)
  } catch (error) {
    console.error('加载省份难度失败', error)
    renderProvinceChart([])
  }
}

function renderProvinceChart(data) {
  if (!provinceChart.value) return
  
  const chart = echarts.init(provinceChart.value)
  
  if (!data || data.length === 0) {
    chart.setOption({
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 16,
          fontWeight: 'normal'
        }
      }
    })
    return
  }
  
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: data.map(item => item.province),
      axisLine: { lineStyle: { color: '#ddd' } },
      axisLabel: { 
        color: '#666',
        rotate: 45 
      }
    },
    yAxis: { 
      type: 'value', 
      name: '平均分',
      axisLine: { lineStyle: { color: '#ddd' } },
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#f0f0f0' } }
    },
    series: [{
      type: 'bar',
      data: data.map(item => item.avg_score),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#83bff6' },
          { offset: 1, color: '#188df0' }
        ])
      }
    }]
  })
}

async function loadPlanDistribution() {
  try {
    const res = await getPlanDistribution()
    const data = res.data && res.data.length > 0 ? res.data.slice(0, 10) : []
    renderPlanChart(data)
  } catch (error) {
    console.error('加载招生计划失败', error)
    renderPlanChart([])
  }
}

function renderPlanChart(data) {
  if (!planChart.value) return
  
  const chart = echarts.init(planChart.value)
  
  if (!data || data.length === 0) {
    chart.setOption({
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 16,
          fontWeight: 'normal'
        }
      }
    })
    return
  }
  
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', right: 10, top: 'center' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
      data: data.map(item => ({
        name: item.province,
        value: item.total_plan
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })
}
</script>

<style scoped>
/* 之前的样式保持不变，这里只添加新增模块的样式 */

/* 热门院校推荐 */
.recommend-section {
  padding: 80px 0;
  background: #f8fafc;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.school-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  opacity: 0;
  transform: translateY(30px);
}

.school-card.animated {
  opacity: 1;
  transform: translateY(0);
}

.school-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
}

.school-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.badge-985 {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
}

.badge-211 {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.badge-other {
  background: linear-gradient(135deg, #a8e6cf, #88d3ce);
}

.school-logo {
  text-align: center;
  margin-bottom: 16px;
}

.school-logo .logo {
  font-size: 48px;
}

.school-info {
  text-align: center;
}

.school-name {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.school-location {
  color: #64748b;
  margin-bottom: 12px;
}

.school-tags {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
}

.school-tags .tag {
  padding: 4px 8px;
  background: #f1f5f9;
  border-radius: 6px;
  font-size: 12px;
  color: #475569;
}

.school-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 16px;
}

.school-stats .stat {
  text-align: center;
}

.school-stats .value {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #3498db;
}

.school-stats .label {
  font-size: 12px;
  color: #94a3b8;
}

.school-hover {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: left 0.3s ease;
}

.school-card:hover .school-hover {
  left: 0;
}

/* 新闻资讯 */
.news-section {
  padding: 80px 0;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.news-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  opacity: 0;
  transform: translateY(30px);
}

.news-card.animated {
  opacity: 1;
  transform: translateY(0);
}

.news-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.news-image {
  text-align: center;
  margin-bottom: 16px;
}

.news-image .image-icon {
  font-size: 48px;
}

.news-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.news-category {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.news-category.政策 {
  background: #ff6b6b;
}

.news-category.招生 {
  background: #4facfe;
}

.news-category.填报 {
  background: #a8e6cf;
}

.news-category.分析 {
  background: #feca57;
}

.news-date {
  font-size: 12px;
  color: #94a3b8;
}

.news-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  line-height: 1.4;
}

.news-desc {
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 16px;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-source {
  font-size: 12px;
  color: #94a3b8;
}

.news-read {
  font-size: 12px;
  color: #94a3b8;
}

.news-hover {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: left 0.3s ease;
}

.news-card:hover .news-hover {
  left: 0;
}

/* 备考指南 */
.guide-section {
  padding: 80px 0;
  background: #f8fafc;
}

.guide-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.guide-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  text-align: center;
  opacity: 0;
  transform: translateY(30px);
}

.guide-card.animated {
  opacity: 1;
  transform: translateY(0);
}

.guide-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
}

.guide-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.guide-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.guide-desc {
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 16px;
}

.guide-tags {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.guide-tags .tag {
  padding: 4px 8px;
  background: #f1f5f9;
  border-radius: 6px;
  font-size: 12px;
  color: #475569;
}

.guide-hover {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: left 0.3s ease;
}

.guide-card:hover .guide-hover {
  left: 0;
}

/* 政策解读 */
.policy-section {
  padding: 80px 0;
}

.policy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.policy-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  opacity: 0;
  transform: translateY(30px);
}

.policy-card.animated {
  opacity: 1;
  transform: translateY(0);
}

.policy-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.policy-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.policy-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
  flex: 1;
}

.policy-date {
  font-size: 12px;
  color: #94a3b8;
  margin-left: 12px;
}

.policy-summary {
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 16px;
}

.policy-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.policy-tags .tag {
  padding: 4px 8px;
  background: #f1f5f9;
  border-radius: 6px;
  font-size: 12px;
  color: #475569;
}

.policy-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.policy-author {
  font-size: 12px;
  color: #94a3b8;
}

.policy-views {
  font-size: 12px;
  color: #94a3b8;
}

.policy-hover {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: left 0.3s ease;
}

.policy-card:hover .policy-hover {
  left: 0;
}

/* 用户评价 */
.testimonials-section {
  padding: 80px 0;
  background: #f8fafc;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.testimonial-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateY(30px);
}

.testimonial-card.animated {
  opacity: 1;
  transform: translateY(0);
}

.testimonial-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.testimonial-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.user-avatar {
  margin-right: 12px;
}

.user-avatar .avatar {
  font-size: 32px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.user-desc {
  font-size: 12px;
  color: #94a3b8;
}

.rating {
  text-align: right;
}

.rating .stars {
  font-size: 14px;
  color: #f59e0b;
}

.testimonial-content {
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 16px;
  font-style: italic;
}

.testimonial-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.testimonial-date {
  font-size: 12px;
  color: #94a3b8;
}

.testimonial-school {
  font-size: 12px;
  color: #3498db;
  font-weight: 600;
}

/* 功能入口 */
.features-section {
  padding: 80px 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.feature-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  text-align: center;
  opacity: 0;
  transform: translateY(30px);
}

.feature-card.animated {
  opacity: 1;
  transform: translateY(0);
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
}

.feature-icon {
  position: relative;
  font-size: 48px;
  margin-bottom: 16px;
}

.feature-icon .icon {
  position: relative;
  z-index: 2;
}

.icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.1;
  transition: all 0.3s ease;
}

.feature-card:hover .icon-glow {
  opacity: 0.2;
  transform: translate(-50%, -50%) scale(1.2);
}

.feature-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.feature-desc {
  color: #64748b;
  line-height: 1.6;
}

.feature-hover {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: left 0.3s ease;
}

.feature-card:hover .feature-hover {
  left: 0;
}

/* 之前的样式保持不变 */
.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  position: relative;
}

/* 加载动画 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
}

.spinner-ring {
  position: absolute;
  width: 64px;
  height: 64px;
  margin: 8px;
  border: 8px solid transparent;
  border-radius: 50%;
  animation: spin 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}

.spinner-ring:nth-child(1) {
  border-top-color: #3498db;
  animation-delay: -0.45s;
}

.spinner-ring:nth-child(2) {
  border-top-color: #9b59b6;
  animation-delay: -0.3s;
}

.spinner-ring:nth-child(3) {
  border-top-color: #2ecc71;
  animation-delay: -0.15s;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #64748b;
  font-size: 16px;
  text-align: center;
}

/* 头部导航 */
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  transition: all 0.3s ease;
}

.header.scrolled {
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.header .container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 24px;
  margin-right: 8px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.nav {
  display: flex;
  gap: 32px;
}

.nav-item {
  color: #64748b;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
  position: relative;
}

.nav-item:hover,
.nav-item.active {
  color: #3498db;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 100%;
  height: 2px;
  background: #3498db;
}

.user-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #3498db, #9b59b6);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

/* 英雄区域 */
.hero {
  padding: 150px 0 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.bg-particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.bg-particle:nth-child(1) {
  width: 100px;
  height: 100px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.bg-particle:nth-child(2) {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.bg-particle:nth-child(3) {
  width: 80px;
  height: 80px;
  bottom: 30%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s ease;
}

.hero-content.animated {
  opacity: 1;
  transform: translateY(0);
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}

.title-line {
  display: block;
}

.title-line.highlight {
  background: linear-gradient(135deg, #ffd700, #ff6b6b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 18px;
  margin-bottom: 32px;
  opacity: 0.9;
}

.search-box {
  margin-bottom: 24px;
}

.search-container {
  display: flex;
  max-width: 500px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.search-container:focus-within {
  background: rgba(255, 255, 255, 0.15);
  transform: scale(1.02);
}

.search-input {
  flex: 1;
  padding: 16px 20px;
  border: none;
  background: transparent;
  color: white;
  font-size: 16px;
  outline: none;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.search-btn {
  padding: 16px 24px;
  background: linear-gradient(135deg, #ffd700, #ff6b6b);
  border: none;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-btn:hover {
  transform: scale(1.05);
}

.quick-tags {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.tag-label {
  font-size: 14px;
  opacity: 0.8;
}

.quick-tags .tag {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s ease;
}

.quick-tags .tag:hover {
  color: white;
}

/* 数据概览 */
.stats-section {
  padding: 80px 0;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s ease;
}

.section-header.animated {
  opacity: 1;
  transform: translateY(0);
}

.section-title {
  font-size: 32px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.section-desc {
  font-size: 16px;
  color: #64748b;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card.animated {
  opacity: 1;
  transform: translateY(0);
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
}

.card-glow {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  transition: left 0.5s ease;
}

.stat-card:hover .card-glow {
  left: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.stat-icon .icon {
  font-size: 24px;
  position: relative;
  z-index: 2;
}

.icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: all 0.3s ease;
}

.stat-card:hover .icon-glow {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1.2);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
}

.stat-trend.up {
  color: #10b981;
}

.stat-trend.down {
  color: #ef4444;
}

.stat-trend.stable {
  color: #6b7280;
}

/* 图表区域 */
.charts-section {
  padding: 80px 0;
  background: #f8fafc;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.chart-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateY(30px);
}

.chart-card.animated {
  opacity: 1;
  transform: translateY(0);
}

.chart-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-icon {
  font-size: 20px;
}

.btn-more {
  background: none;
  border: none;
  color: #3498db;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;
}

.btn-more:hover {
  gap: 8px;
}

.chart-controls {
  display: flex;
  gap: 12px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  color: #64748b;
}

.chart-container {
  height: 300px;
}

.chart {
  width: 100%;
  height: 100%;
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rank-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
  overflow: hidden;
}

.rank-item:hover {
  background: #f1f5f9;
}

.rank-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rank-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.rank-1 {
  background: #ff6b6b;
}

.rank-2 {
  background: #4facfe;
}

.rank-3 {
  background: #a8e6cf;
}

.rank-other {
  background: #94a3b8;
}

.rank-name {
  font-weight: 500;
  color: #1e293b;
}

.rank-score {
  text-align: right;
}

.score {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.score-label {
  font-size: 12px;
  color: #94a3b8;
}

.rank-hover {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: left 0.3s ease;
}

.rank-item:hover .rank-hover {
  left: 0;
}

.empty {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content {
  text-align: center;
  color: #94a3b8;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
}

/* 底部 */
.footer {
  background: #1e293b;
  color: white;
  padding: 60px 0 20px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  margin-bottom: 40px;
}

.footer-section h4 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
}

.footer-section p {
  color: #94a3b8;
  line-height: 1.6;
}

.social-links {
  display: flex;
  gap: 16px;
}

.social-link {
  color: #94a3b8;
  text-decoration: none;
  transition: color 0.3s ease;
}

.social-link:hover {
  color: white;
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #334155;
}

.footer-bottom p {
  color: #94a3b8;
  font-size: 14px;
}

/* 回到顶部按钮 */
.back-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 20px;
  cursor: pointer;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
}

.back-to-top.visible {
  opacity: 1;
  visibility: visible;
}

.back-to-top:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }
  
  .nav {
    gap: 16px;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card.full-width {
    grid-column: 1;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .recommend-grid,
  .news-grid,
  .guide-grid,
  .policy-grid,
  .testimonials-grid,
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .search-container {
    flex-direction: column;
  }
  
  .search-input {
    padding: 12px 16px;
  }
  
  .search-btn {
    padding: 12px 16px;
    justify-content: center;
  }
}
</style>