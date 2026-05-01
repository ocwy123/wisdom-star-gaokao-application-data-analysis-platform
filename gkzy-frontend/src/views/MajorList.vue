<template>
  <div class="major-list-page">
    <Header />

    <!-- 主体内容 -->
    <main class="main-content">
      <div class="container">
        <!-- 筛选区域 -->
        <div class="filter-section">
          <h1 class="page-title">专业查询</h1>
          
          <!-- 搜索框 -->
          <div class="search-box">
            <el-input 
              v-model="filters.keyword" 
              placeholder="搜索专业名称或代码"
              class="keyword-input"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
          </div>

          <!-- 重置按钮 -->
          <div class="filter-actions">
            <el-button @click="handleReset">重置筛选</el-button>
          </div>
        </div>

        <!-- 专业列表 -->
        <div class="major-grid">
          <div v-if="loading" class="loading-state">
            <el-icon class="is-loading" :size="32"><Loading /></el-icon>
            <p>加载中...</p>
          </div>
          
          <div class="major-card" v-else v-for="major in majorList" :key="major.id" @click="viewDetail(major.id)">
            <div class="major-header">
              <div class="major-info">
                <h3 class="major-name">{{ major.name || '未知专业' }}</h3>
                <p class="major-code">代码：{{ major.code || '-' }}</p>
              </div>
            </div>

            <div class="major-tags">
              <el-tag v-if="major.degree" type="primary" size="small" effect="plain">{{ major.degree }}</el-tag>
              <el-tag type="info" size="small" effect="plain">{{ major.duration || '-' }}年制</el-tag>
              <el-tag v-if="major.subjects" type="success" size="small" effect="plain">{{ major.subjects }}</el-tag>
            </div>

            <div class="major-footer">
              <span class="view-detail">查看详情 →</span>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty v-if="majorList.length === 0 && !loading" description="暂无数据" />

        <!-- 分页 -->
        <div class="pagination-container" v-if="pagination.total > 0">
          <el-pagination
            v-model:current-page="pagination.page"
            :page-size="pagination.page_size"
            :page-sizes="[20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Loading } from '@element-plus/icons-vue'
import { getMajorList } from '@/api/major'
import Header from '@/components/Header.vue'

const router = useRouter()

// 用户登录状态
const isLoggedIn = ref(false)
const userInfo = ref(null)

// 搜索
const miniSearch = ref('')

// 筛选条件
const filters = reactive({
  keyword: ''
})

// 数据
const majorList = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
  total_pages: 0
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
      console.error('解析token失败:', error)
    }
  } else {
    isLoggedIn.value = false
    userInfo.value = null
  }
}

// 登录注册相关函数
const handleLogin = () => {
  console.log('登录按钮被点击')
  router.push('/login').then(() => {
    console.log('成功跳转到登录页面')
  }).catch(err => {
    console.error('跳转失败:', err)
  })
}

const handleRegister = () => {
  console.log('注册按钮被点击')
  router.push('/register').then(() => {
    console.log('成功跳转到注册页面')
  }).catch(err => {
    console.error('跳转失败:', err)
  })
}

const handleLogout = () => {
  console.log('退出登录')
  localStorage.removeItem('userToken')
  localStorage.removeItem('adminToken')
  
  isLoggedIn.value = false
  userInfo.value = null
  
  router.push('/').then(() => {
    console.log('退出登录成功，跳转到首页')
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

// 加载专业列表
const loadMajorList = async () => {
  loading.value = true
  
  try {
    const params = {
      page: pagination.page,
      size: pagination.page_size,
      keyword: filters.keyword || undefined
    }

    const res = await getMajorList(params)
    
    const responseData = res.data
    
    if (responseData) {
      majorList.value = responseData.list || responseData.data || []
      pagination.total = responseData.total || 0
      pagination.page = responseData.page || 1
      pagination.page_size = responseData.size || responseData.page_size || 20
      pagination.total_pages = responseData.total_pages || Math.ceil(pagination.total / pagination.page_size)
    } else {
      majorList.value = []
      pagination.total = 0
    }
  } catch (error) {
    ElMessage.error('加载专业列表失败')
    console.error('[错误] 加载专业列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  pagination.page = 1
  loadMajorList()
}

// 重置筛选
const handleReset = () => {
  filters.keyword = ''
  pagination.page = 1
  loadMajorList()
}

// 分页变化处理
const handleSizeChange = async (size) => {
  pagination.page_size = size
  pagination.page = 1
  await loadMajorList()
}

const handleCurrentChange = async (page) => {
  await loadMajorList()
}

// 查看详情
const viewDetail = (id) => {
  router.push(`/major/${id}?from=majors`)
}

// 初始化
onMounted(() => {
  checkLoginStatus()
  loadMajorList()
})
</script>

<style scoped>
.major-list-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 主体内容 */
.main-content {
  padding: 40px 0;
  min-height: calc(100vh - 400px);
}

/* 筛选区域 */
.filter-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 24px 0;
}

.search-box {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.keyword-input {
  flex: 1;
}

.keyword-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e4e7ed inset;
}

.keyword-input :deep(.el-input__wrapper:hover),
.keyword-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #667eea inset;
}

.filter-actions {
  padding-top: 24px;
  border-top: 1px solid #e4e7ed;
}

/* 加载状态 */
.loading-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #999;
}

.loading-state p {
  margin-top: 12px;
  font-size: 14px;
}

/* 专业列表 */
.major-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.major-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e4e7ed;
}

.major-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  border-color: #667eea;
}

.major-header {
  margin-bottom: 16px;
}

.major-info {
  width: 100%;
}

.major-name {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.major-code {
  font-size: 13px;
  color: #999;
  margin: 0;
}

.major-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.major-footer {
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

.major-card:hover .view-detail {
  color: #764ba2;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

/* 响应式 */
@media (max-width: 768px) {
  .major-grid {
    grid-template-columns: 1fr;
  }
}
</style>
