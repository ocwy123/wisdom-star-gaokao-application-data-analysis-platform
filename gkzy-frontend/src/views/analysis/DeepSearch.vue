<template>
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
          <router-link to="/志愿" class="nav-item">志愿填报</router-link>
          <router-link to="/analysis/multi-dimension" class="nav-item">多维分析</router-link>
          <router-link to="/analysis/deep-search" class="nav-item active">深度检索</router-link>
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

  <div class="deep-search">
    <!-- 搜索头部 -->
    <div class="search-header">
      <h2>深度信息检索</h2>
      <div class="search-box">
        <el-input v-model="searchKeyword" placeholder="输入关键词搜索学校、专业、就业信息..." size="large" @keyup.enter="handleSearch">
          <template #append>
            <el-button type="primary" @click="handleSearch" :loading="searching">
              <el-icon>
                <Search />
              </el-icon> 搜索
            </el-button>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 筛选面板 -->
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <span>高级筛选</span>
          <el-button type="text" @click="resetFilters">重置</el-button>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <div class="filter-item">
            <label>检索类型</label>
            <el-checkbox-group v-model="searchTypes">
              <el-checkbox label="school">学校</el-checkbox>
              <el-checkbox label="major">专业</el-checkbox>
              <el-checkbox label="employment">就业</el-checkbox>
              <el-checkbox label="admission">招生</el-checkbox>
              <el-checkbox label="heat">热度</el-checkbox>
            </el-checkbox-group>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="filter-item">
            <label>省份</label>
            <el-select v-model="filters.province" placeholder="全部" clearable filterable>
              <el-option v-for="province in filterOptions.provinces" :key="province" :label="province"
                :value="province" />
            </el-select>
          </div>

          <div class="filter-item">
            <label>学校类型</label>
            <el-select v-model="filters.school_type" placeholder="全部" clearable>
              <el-option v-for="type in filterOptions.school_types" :key="type" :label="type" :value="type" />
            </el-select>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="filter-item">
            <label>年份</label>
            <el-select v-model="filters.year" placeholder="全部" clearable>
              <el-option v-for="year in filterOptions.years" :key="year" :label="year" :value="year" />
            </el-select>
          </div>

          <div class="filter-item">
            <label>分数范围</label>
            <el-slider v-model="scoreRange" range :min="0" :max="750" :marks="scoreMarks" @change="updateScoreRange" />
          </div>
        </el-col>

        <el-col :span="6">
          <div class="filter-item">
            <label>985/211</label>
            <el-checkbox v-model="filters.is_985">985院校</el-checkbox>
            <el-checkbox v-model="filters.is_211">211院校</el-checkbox>
          </div>

          <div class="filter-item">
            <label>排序方式</label>
            <el-radio-group v-model="sortBy">
              <el-radio label="relevance">相关度</el-radio>
              <el-radio label="heat_score">热度</el-radio>
              <el-radio label="avg_salary">薪资</el-radio>
              <el-radio label="min_score">分数</el-radio>
            </el-radio-group>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 搜索结果 -->
    <el-card class="result-card">
      <template #header>
        <div class="card-header">
          <span>搜索结果 ({{ total }}条)</span>
          <div>
            <el-button-group>
              <el-button :type="viewMode === 'list' ? 'primary' : 'default'" @click="viewMode = 'list'">
                <el-icon>
                  <List />
                </el-icon> 列表
              </el-button>
              <el-button :type="viewMode === 'card' ? 'primary' : 'default'" @click="viewMode = 'card'">
                <el-icon>
                  <Grid />
                </el-icon> 卡片
              </el-button>
              <!-- <el-button :type="viewMode === 'chart' ? 'primary' : 'default'" @click="viewMode = 'chart'">
                <el-icon><DataLine /></el-icon> 图表
              </el-button> -->
            </el-button-group>
            <el-button @click="exportResults" style="margin-left: 10px;">
              <el-icon>
                <Download />
              </el-icon> 导出
            </el-button>
          </div>
        </div>
      </template>

      <!-- 列表视图 -->
      <div v-if="viewMode === 'list'">
        <el-table :data="results" border stripe v-loading="searching">
          <el-table-column prop="type" label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getTypeTag(row.type)">
                {{ getTypeName(row.type) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="name" label="名称" min-width="200">
            <template #default="{ row }">
              <div class="result-name">
                <span v-html="highlightKeyword(row.name || row.school_name || row.major_name || '')"></span>
                <el-tag v-if="row.is_985" size="small" type="danger" class="school-tag">985</el-tag>
                <el-tag v-if="row.is_211" size="small" type="warning" class="school-tag">211</el-tag>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="province" label="省份" width="120" />

          <el-table-column prop="heat_score" label="热度" width="100">
            <template #default="{ row }">
              <el-rate v-model="row.heat_score" :max="5" :allow-half="true" disabled text-color="#ff9900" />
            </template>
          </el-table-column>

          <el-table-column prop="avg_salary" label="平均薪资" width="120">
            <template #default="{ row }">
              {{ row.avg_salary ? '¥' + row.avg_salary.toLocaleString() : '-' }}
            </template>
          </el-table-column>

          <el-table-column prop="min_score" label="最低分数" width="100">
            <template #default="{ row }">
              {{ row.min_score || '-' }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="viewDetail(row)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 卡片视图 -->
      <div v-else-if="viewMode === 'card'" class="card-view">
        <el-row :gutter="20">
          <el-col :span="6" v-for="item in results" :key="item.id">
            <el-card class="result-card-item" shadow="hover">
              <div class="card-type">
                <el-tag :type="getTypeTag(item.type)" size="small">
                  {{ getTypeName(item.type) }}
                </el-tag>
              </div>
              <div class="card-title">{{ item.name || item.school_name || item.major_name }}</div>
              <div class="card-info">
                <div v-if="item.province">📍 {{ item.province }}</div>
                <div v-if="item.avg_salary">💰 ¥{{ item.avg_salary.toLocaleString() }}</div>
                <div v-if="item.heat_score">🔥 {{ item.heat_score }}分</div>
                <div v-if="item.min_score">📊 {{ item.min_score }}分</div>
              </div>
              <div class="card-actions">
                <el-button type="primary" link @click="viewDetail(item)">查看详情</el-button>
                <el-button type="primary" link @click="addToCompare(item)">加入对比</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 图表视图 -->
      <div v-else-if="viewMode === 'chart'" class="chart-view">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>热度分布</span>
              </template>
              <div ref="heatChart" style="height: 300px"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>分数分布</span>
              </template>
              <div ref="scoreChart" style="height: 300px"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total"
          :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" @size-change="handleSearch"
          @current-change="handleSearch" />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" :title="detailTitle" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item v-for="(value, key) in detailData" :key="key" :label="key">
          {{ value }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, List, Grid, DataLine, Download } from '@element-plus/icons-vue'
import request from '@/utils/request'
import * as echarts from 'echarts'

export default {
  name: 'DeepSearch',
  components: {
    Search, List, Grid, DataLine, Download
  },
  setup() {
    const router = useRouter()

    // 导航栏相关
    const isLoggedIn = ref(false)
    const userInfo = ref(null)

    // 检查登录状态
    const checkLoginStatus = () => {
      const token = localStorage.getItem('userToken')
      const user = localStorage.getItem('userInfo')
      if (token && user) {
        isLoggedIn.value = true
        userInfo.value = JSON.parse(user)
      }
    }

    // 滚动到顶部
    const scrollToTop = () => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    // 处理登录
    const handleLogin = () => {
      router.push('/login')
    }

    // 处理注册
    const handleRegister = () => {
      router.push('/register')
    }

    // 跳转到个人中心
    const goToProfile = () => {
      router.push('/profile')
    }

    // 处理登出
    const handleLogout = () => {
      localStorage.removeItem('userToken')
      localStorage.removeItem('userInfo')
      isLoggedIn.value = false
      userInfo.value = null
      ElMessage.success('已退出登录')
      router.push('/')
    }

    // 在挂载时检查登录状态
    onMounted(() => {
      checkLoginStatus()
      fetchFilterOptions()
    })
    const searchKeyword = ref('')
    const searching = ref(false)
    const results = ref([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(20)
    const viewMode = ref('list')

    // 搜索类型
    const searchTypes = ref(['school', 'major', 'employment', 'admission', 'heat'])

    // 筛选条件
    const filters = reactive({
      province: '',
      school_type: '',
      year: '',
      is_985: false,
      is_211: false
    })

    const scoreRange = ref([0, 750])
    const sortBy = ref('relevance')

    // 筛选选项
    const filterOptions = ref({
      provinces: [],
      school_types: [],
      years: []
    })

    const scoreMarks = {
      0: '0',
      400: '400',
      500: '500',
      600: '600',
      750: '750'
    }

    // 详情相关
    const detailVisible = ref(false)
    const detailTitle = ref('')
    const detailData = ref({})

    // 获取筛选选项
    const fetchFilterOptions = async () => {
      try {
        const res = await request.get('/analysis/filters')
        if (res.data.success) {
          filterOptions.value = res.data.data
        }
      } catch (error) {
        console.error('获取筛选选项失败:', error)
      }
    }

    // 搜索
    const handleSearch = async () => {
      if (!searchKeyword.value) {
        ElMessage.warning('请输入搜索关键词')
        return
      }

      searching.value = true
      try {
        const res = await request.post('/analysis/search', {
          keyword: searchKeyword.value,
          types: searchTypes.value,
          filters: {
            ...filters,
            score_range: scoreRange.value
          },
          page: currentPage.value,
          page_size: pageSize.value,
          sort_by: sortBy.value,
          sort_order: 'desc'
        })

        if (res.data.success) {
          results.value = res.data.data.items
          total.value = res.data.data.total

          // 更新图表
          if (viewMode.value === 'chart') {
            nextTick(() => {
              initCharts()
            })
          }
        }
      } catch (error) {
        ElMessage.error('搜索失败')
      } finally {
        searching.value = false
      }
    }

    // 重置筛选
    const resetFilters = () => {
      filters.province = ''
      filters.school_type = ''
      filters.year = ''
      filters.is_985 = false
      filters.is_211 = false
      scoreRange.value = [0, 750]
      sortBy.value = 'relevance'
      searchTypes.value = ['school', 'major', 'employment', 'admission', 'heat']
    }

    // 更新分数范围
    const updateScoreRange = (value) => {
      scoreRange.value = value
    }

    // 获取类型标签
    const getTypeTag = (type) => {
      const map = {
        'school': 'success',
        'major': 'warning',
        'employment': 'info',
        'admission': 'primary',
        'heat': 'danger'
      }
      return map[type] || 'info'
    }

    // 获取类型名称
    const getTypeName = (type) => {
      const map = {
        'school': '学校',
        'major': '专业',
        'employment': '就业',
        'admission': '招生',
        'heat': '热度'
      }
      return map[type] || type
    }

    // 高亮关键词
    const highlightKeyword = (text) => {
      if (!text || !searchKeyword.value) return text
      const regex = new RegExp(searchKeyword.value, 'gi')
      return text.replace(regex, '<span class="highlight">$&</span>')
    }

    // 查看详情
    const viewDetail = (row) => {
      detailTitle.value = row.name || row.school_name || row.major_name
      detailData.value = row
      detailVisible.value = true
    }

    // 加入对比
    const addToCompare = (item) => {
      // 存储到 localStorage 或 store
      const compareList = JSON.parse(localStorage.getItem('compareList') || '[]')
      compareList.push(item)
      localStorage.setItem('compareList', JSON.stringify(compareList))
      ElMessage.success('已加入对比列表')
    }

    // 导出结果
    const exportResults = async () => {
      try {
        const res = await request.post('/analysis/export', {
          type: 'csv',
          data: results.value
        })

        if (res.data.success) {
          const blob = new Blob([res.data.data], { type: 'text/csv' })
          const link = document.createElement('a')
          link.href = URL.createObjectURL(blob)
          link.download = `search_results_${new Date().getTime()}.csv`
          link.click()
          ElMessage.success('导出成功')
        }
      } catch (error) {
        ElMessage.error('导出失败')
      }
    }

    // 初始化图表
    const heatChart = ref(null)
    const scoreChart = ref(null)

    const initCharts = () => {
      if (heatChart.value) {
        const chart = echarts.init(heatChart.value)
        chart.setOption({
          title: { text: '热度分布' },
          tooltip: { trigger: 'axis' },
          xAxis: {
            type: 'category',
            data: results.value.slice(0, 10).map(item =>
              item.name || item.school_name || item.major_name
            )
          },
          yAxis: { type: 'value' },
          series: [{
            data: results.value.slice(0, 10).map(item => item.heat_score || 0),
            type: 'bar',
            name: '热度'
          }]
        })
      }

      if (scoreChart.value) {
        const chart = echarts.init(scoreChart.value)
        chart.setOption({
          title: { text: '分数分布' },
          tooltip: { trigger: 'axis' },
          xAxis: {
            type: 'category',
            data: results.value.slice(0, 10).map(item =>
              item.name || item.school_name || item.major_name
            )
          },
          yAxis: { type: 'value' },
          series: [{
            data: results.value.slice(0, 10).map(item => item.min_score || 0),
            type: 'line',
            name: '最低分数'
          }]
        })
      }
    }

    onMounted(() => {
      fetchFilterOptions()
    })

    return {
      // 导航栏相关
      isLoggedIn,
      userInfo,
      scrollToTop,
      handleLogin,
      handleRegister,
      goToProfile,
      handleLogout,
      searchKeyword,
      searching,
      results,
      total,
      currentPage,
      pageSize,
      viewMode,
      searchTypes,
      filters,
      scoreRange,
      sortBy,
      filterOptions,
      scoreMarks,
      detailVisible,
      detailTitle,
      detailData,
      heatChart,
      scoreChart,
      handleSearch,
      resetFilters,
      updateScoreRange,
      getTypeTag,
      getTypeName,
      highlightKeyword,
      viewDetail,
      addToCompare,
      exportResults
    }
  }
}
</script>

<style scoped>
.deep-search {
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  min-height: 100vh;
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
  color: #1a1a1a;
  background: #f0f0f0;
}

.btn-primary {
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
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

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  width: 100%;
}

/* 搜索头部 */
.search-header {
  margin-bottom: 30px;
  padding: 30px 0 20px 0;
  border-bottom: 1px solid #e8e8e8;
  text-align: center;
}

.search-header h2 {
  margin-bottom: 20px;
  color: #1a1a1a;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.search-box {
  max-width: 800px;
  margin: 0 auto;
}

.search-box :deep(.el-input-group__append) {
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  border: none;
}

.search-box :deep(.el-input-group__append .el-button) {
  color: white;
  font-weight: 600;
}

/* 卡片样式 */
.filter-card,
.result-card {
  margin-bottom: 24px;
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.filter-card:hover,
.result-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header span {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.card-header .el-button {
  color: #1e88e5;
  font-weight: 500;
}

.card-header .el-button:hover {
  color: #1565c0;
}

/* 筛选器样式 */
.filter-item {
  margin-bottom: 20px;
}

.filter-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #666;
}

.filter-item :deep(.el-checkbox-group) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-item :deep(.el-checkbox) {
  margin-right: 0;
}

.filter-item :deep(.el-checkbox__label) {
  font-weight: 500;
}

.filter-item :deep(.el-select),
.filter-item :deep(.el-slider) {
  width: 100%;
}

/* 搜索结果样式 */
.result-card {
  min-height: 500px;
}

.result-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.school-tag {
  margin-left: 5px;
}

.highlight {
  background-color: #ffeb3b;
  font-weight: bold;
  padding: 0 2px;
  border-radius: 3px;
}

/* 卡片视图 */
.card-view {
  margin-top: 20px;
}

.result-card-item {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.result-card-item:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.card-type {
  position: absolute;
  top: 10px;
  right: 10px;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  padding-right: 60px;
  color: #1a1a1a;
}

.card-info {
  font-size: 13px;
  color: #666;
  margin-bottom: 10px;
}

.card-info div {
  margin-bottom: 5px;
}

.card-actions {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid #eee;
  padding-top: 10px;
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table__header) {
  background: linear-gradient(135deg, #f5f7fa 0%, #e3f2fd 100%);
}

:deep(.el-table th) {
  background: transparent;
  color: #1a1a1a;
  font-weight: 600;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: #f8f9fa;
}

:deep(.el-table .el-table__row:hover td) {
  background: #e3f2fd;
}

:deep(.el-tag) {
  font-weight: 500;
}

:deep(.el-rate) {
  display: inline-flex;
}

/* 分页样式 */
:deep(.el-pagination) {
  margin-top: 20px;
  justify-content: center;
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
}

/* 按钮组样式 */
:deep(.el-button-group) {
  display: flex;
  gap: 0;
}

:deep(.el-button-group .el-button) {
  border-radius: 0;
}

:deep(.el-button-group .el-button:first-child) {
  border-radius: 6px 0 0 6px;
}

:deep(.el-button-group .el-button:last-child) {
  border-radius: 0 6px 6px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .deep-search {
    padding: 16px;
  }

  .search-header {
    padding: 20px 0 15px 0;
  }

  .search-header h2 {
    font-size: 24px;
  }

  .search-box {
    max-width: 100%;
  }

  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .filter-item :deep(.el-checkbox-group) {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .result-name {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>