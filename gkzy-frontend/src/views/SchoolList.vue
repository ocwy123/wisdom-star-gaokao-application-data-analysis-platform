<template>
  <div class="school-list-page">
    <Header />

    <!-- 主体内容 -->
    <main class="main-content">
      <div class="container">
        <!-- 筛选区域 -->
        <div class="filter-section">
          <h1 class="page-title">高校查询</h1>
          
          <!-- 搜索框 -->
          <div class="search-box">
            <el-input 
              v-model="filters.keyword" 
              placeholder="搜索高校名称、省份、城市或类型"
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

          <!-- 筛选条件 -->
          <div class="filter-tags">
            <div class="filter-item">
              <span class="filter-label">省份：</span>
              <el-select v-model="filters.province" placeholder="全部省份" clearable @change="handleProvinceChange" class="filter-select">
                <el-option
                  v-for="item in provinces"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </div>

            <div class="filter-item">
              <span class="filter-label">城市：</span>
              <el-select v-model="filters.city" placeholder="全部城市" clearable class="filter-select">
                <el-option
                  v-for="item in cities"
                  :key="item.city"
                  :label="item.city"
                  :value="item.city"
                />
              </el-select>
            </div>

            <div class="filter-item">
              <span class="filter-label">类型：</span>
              <el-select v-model="filters.type" placeholder="全部类型" clearable class="filter-select">
                <el-option
                  v-for="item in schoolTypes"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </div>

            <div class="filter-item">
              <span class="filter-label">标签：</span>
              <el-checkbox-group v-model="filters.tags" @change="handleTagChange">
                <el-checkbox label="985" border>985</el-checkbox>
                <el-checkbox label="211" border>211</el-checkbox>
                <el-checkbox label="双一流" border>双一流</el-checkbox>
              </el-checkbox-group>
            </div>
          </div>

          <!-- 重置按钮 -->
          <div class="filter-actions">
            <el-button @click="handleReset">重置筛选</el-button>
          </div>
        </div>

        <!-- 高校列表 -->
        <div class="school-grid">
          <div class="school-card" v-for="school in schoolList" :key="school.id" @click="viewDetail(school.id)">
            <div class="school-header">
              <div class="school-logo" v-if="school.logo">
                <img :src="school.logo" :alt="school.name || '学校'" />
              </div>
              <div class="school-logo-placeholder" v-else>
                <span>{{ school.name ? school.name.charAt(0) : '校' }}</span>
              </div>
              <div class="school-info">
                <h3 class="school-name">{{ school.name || '未知学校' }}</h3>
                <p class="school-location">
                  <el-icon><Location /></el-icon>
                  {{ school.province || '' }} · {{ school.city || '' }}
                </p>
              </div>
            </div>

            <div class="school-tags">
              <el-tag v-if="school.is_985" type="danger" size="small" effect="plain">985</el-tag>
              <el-tag v-if="school.is_211" type="warning" size="small" effect="plain">211</el-tag>
              <el-tag v-if="school.is_double_first" type="success" size="small" effect="plain">双一流</el-tag>
              <el-tag type="info" size="small" effect="plain">{{ school.type || '' }}</el-tag>
            </div>

            <div class="school-stats">
              <div class="stat-item">
                <span class="stat-label">博士点</span>
                <span class="stat-value">{{ school.phd_count || '-' }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">硕士点</span>
                <span class="stat-value">{{ school.master_count || '-' }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">建校时间</span>
                <span class="stat-value">{{ school.founded_year || '-' }}</span>
              </div>
            </div>

            <div class="school-footer">
              <span class="school-code">代码：{{ school.code || '-' }}</span>
              <span class="view-detail">查看详情 →</span>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty v-if="schoolList.length === 0 && !loading" description="暂无数据" />

        <!-- 分页 -->
        <div class="pagination-container" v-if="pagination.total > 0">
          <el-pagination
            v-model:current-page="pagination.page"
            :page-size="pagination.page_size"
            :page-sizes="[10, 21, 50, 100]"
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
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Location } from '@element-plus/icons-vue'
import { getSchoolList, getProvinces, getCities, getSchoolTypes } from '@/api/school'
import Header from '@/components/Header.vue'

const router = useRouter()

// 用户登录状态
const isLoggedIn = ref(false)
const userInfo = ref(null)

// 搜索
const miniSearch = ref('')

// 筛选条件
const filters = reactive({
  keyword: '',
  province: '',
  city: '',
  type: '',
  tags: []
})

// 数据
const schoolList = ref([])
const provinces = ref([])
const cities = ref([])
const schoolTypes = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  page_size: 21,
  total: 0,
  total_pages: 0
})

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

// 登录注册相关函数
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

// 加载高校列表
const loadSchoolList = async () => {
  loading.value = true
  console.log('[加载数据] 开始加载，当前参数:', { 
    page: pagination.page, 
    page_size: pagination.page_size,
    filters: filters 
  })
  
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      keyword: filters.keyword || undefined,
      province: filters.province || undefined,
      city: filters.city || undefined,
      type: filters.type || undefined,
      is_985: filters.tags.includes('985') ? true : undefined,
      is_211: filters.tags.includes('211') ? true : undefined,
      is_double_first: filters.tags.includes('双一流') ? true : undefined
    }

    console.log('[API] 请求参数:', params)
    const res = await getSchoolList(params)
    console.log('[API] 完整响应:', JSON.stringify(res, null, 2))
    
    // 后端返回格式：{ code: 200, data: { list: [...], total: 100, ... }, message: 'success' }
    const responseData = res.data
    
    if (responseData) {
      console.log('[数据] 响应数据 data 字段:', responseData)
      // 注意：responseData 可能直接就是 { list, total, ... }，也可能是嵌套的
      const actualData = responseData.list ? responseData : (responseData.data || {})
      console.log('[数据] 实际数据:', actualData)
      
      schoolList.value = actualData.list || actualData.data || []
      pagination.total = actualData.total || 0
      pagination.page = actualData.page || 1
      pagination.page_size = actualData.page_size || 20
      pagination.total_pages = actualData.total_pages || Math.ceil(pagination.total / pagination.page_size)
      
      console.log('[数据] 赋值完成:', { 
        schoolListCount: schoolList.value.length, 
        total: pagination.total, 
        page: pagination.page, 
        page_size: pagination.page_size,
        total_pages: pagination.total_pages
      })
    } else {
      console.warn('[警告] 响应数据为空')
      schoolList.value = []
      pagination.total = 0
    }
  } catch (error) {
    ElMessage.error('加载高校列表失败')
    console.error('[错误] 加载高校列表失败:', error)
    console.error('[错误详情]:', error.response?.data || error.message)
  } finally {
    loading.value = false
    console.log('[加载数据] 加载完成')
  }
}

// 加载省份列表
const loadProvinces = async () => {
  try {
    const res = await getProvinces()
    if (res.data && res.data.data) {
      provinces.value = res.data.data
    }
  } catch (error) {
    console.error('加载省份列表失败:', error)
  }
}

// 加载城市列表
const loadCities = async (province) => {
  try {
    console.log('[加载城市] 请求省份:', province)
    const res = await getCities(province)
    console.log('[加载城市] 响应数据:', res)
    if (res.data && res.data.data) {
      cities.value = res.data.data
      console.log('[加载城市] 城市列表已更新:', cities.value)
    }
  } catch (error) {
    console.error('[加载城市] 失败:', error)
    throw error
  }
}

// 加载学校类型列表
const loadSchoolTypes = async () => {
  try {
    const res = await getSchoolTypes()
    if (res.data && res.data.data) {
      schoolTypes.value = res.data.data
    }
  } catch (error) {
    console.error('加载学校类型列表失败:', error)
  }
}

// 搜索处理
const handleSearch = () => {
  pagination.page = 1
  loadSchoolList()
}

// 省份变化处理
const handleProvinceChange = async (province) => {
  console.log('[省份变化] 选择的省份:', province)
  console.log('[省份变化] filters.province 当前值:', filters.province)
  filters.city = ''  // 清空城市选择
  if (province) {
    await loadCities(province)
    console.log('[省份变化] 城市列表已更新:', cities.value.length, '个城市')
  } else {
    cities.value = []
    console.log('[省份变化] 省份为空，清空城市列表')
  }
}

// 标签变化处理
const handleTagChange = (tags) => {
  // 处理标签逻辑
}

// 重置筛选
const handleReset = () => {
  filters.keyword = ''
  filters.province = ''
  filters.city = ''
  filters.type = ''
  filters.tags = []
  pagination.page = 1
  cities.value = []
  loadSchoolList()
}

// 分页变化处理 - 使用 async/await 确保数据更新
const handleSizeChange = async (size) => {
  console.log('[分页] size-change 触发:', size)
  pagination.page_size = size
  pagination.page = 1  // 切换每页数量时重置为第 1 页
  console.log('[分页] 准备加载数据，参数:', { page: pagination.page, page_size: pagination.page_size })
  await loadSchoolList()
}

const handleCurrentChange = async (page) => {
  console.log('[分页] current-change 触发:', page)
  // pagination.page 已经自动更新为 page（由 v-model 处理）
  console.log('[分页] 准备加载数据，参数:', { page: pagination.page, page_size: pagination.page_size })
  await loadSchoolList()
}

// 查看详情
const viewDetail = (id) => {
  // TODO: 跳转到详情页
  // ElMessage.info('详情页开发中...')
  console.log(id)
  router.push(`/school/${id}`)
}

// 回到顶部
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 监听筛选条件变化
watch(() => filters.type, () => {
  handleSearch()
})

// 初始化
onMounted(() => {
  checkLoginStatus()
  loadSchoolList()
  loadProvinces()
  loadSchoolTypes()
})
</script>

<style scoped>
.school-list-page {
  min-height: 100vh;
  background: #f5f7fa;
}

/* 头部样式 - 与首页保持一致 */
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

.filter-tags {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.filter-label {
  font-size: 14px;
  color: #666;
  min-width: 60px;
  font-weight: 500;
}

.filter-select {
  width: 200px;
}

.filter-actions {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e4e7ed;
}

/* 高校列表 */
.school-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

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
  justify-content: center;
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
  grid-template-columns: repeat(3, 1fr);
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

.school-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.school-code {
  font-size: 12px;
  color: #999;
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

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

/* 底部 */
.footer {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 48px 0 24px;
  margin-top: 60px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  margin-bottom: 40px;
}

.footer-col {
  min-width: 250px;
}

.footer-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 20px 0;
  color: white;
}

.footer-desc {
  font-size: 14px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 12px;
}

.footer-links a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: white;
}

.footer-bottom {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.footer-bottom p {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
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

  .filter-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-select {
    width: 100%;
  }
}
</style>
