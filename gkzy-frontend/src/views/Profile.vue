<template>
  <div class="profile-container">
    
    <Header />

    <div class="profile-header">
      <h2>个人中心</h2>
    </div>
    
    <div class="profile-content">
      <el-card class="profile-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>
        
        <el-form :model="profileForm" :rules="rules" ref="profileFormRef" label-width="100px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="profileForm.username" disabled />
          </el-form-item>
          
          <el-form-item label="昵称" prop="nickname">
            <el-input v-model="profileForm.nickname" />
          </el-form-item>
          
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="profileForm.email" />
          </el-form-item>
          
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="profileForm.phone" />
          </el-form-item>
          
          <el-form-item label="注册时间">
            <span>{{ profileForm.register_time }}</span>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" :loading="profileLoading" @click="updateProfile">
              保存修改
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <el-card class="password-card">
        <template #header>
          <div class="card-header">
            <span>修改密码</span>
          </div>
        </template>
        
        <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
          <el-form-item label="原密码" prop="oldPassword">
            <el-input v-model="passwordForm.oldPassword" type="password" show-password />
          </el-form-item>
          
          <el-form-item label="新密码" prop="newPassword">
            <el-input v-model="passwordForm.newPassword" type="password" show-password />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
          </el-form-item>
          
          <el-form-item>
            <el-button type="warning" :loading="passwordLoading" @click="changePassword">
              修改密码
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 收藏管理 -->
      <el-card class="favorite-card">
        <template #header>
          <div class="card-header">
            <span>我的收藏</span>
            <div class="tab-buttons">
              <el-button :type="activeFavoriteTab === 'all' ? 'primary' : 'default'" @click="activeFavoriteTab = 'all'">全部</el-button>
              <el-button :type="activeFavoriteTab === 'school' ? 'primary' : 'default'" @click="activeFavoriteTab = 'school'">高校</el-button>
              <el-button :type="activeFavoriteTab === 'major' ? 'primary' : 'default'" @click="activeFavoriteTab = 'major'">专业</el-button>
            </div>
          </div>
        </template>
        
        <div class="favorite-list">
          <div v-if="favoritesLoading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          
          <div v-else-if="filteredFavorites.length === 0" class="empty-container">
            <el-empty description="暂无收藏内容" />
          </div>
          
          <div v-else class="favorites-grid">
            <div v-for="favorite in filteredFavorites" :key="favorite.id" class="favorite-item">
              <div class="favorite-content">
                <div class="favorite-type">
                  <el-tag :type="favorite.favorite_type === 'school' ? 'success' : 'primary'">
                    {{ favorite.favorite_type === 'school' ? '高校' : '专业' }}
                  </el-tag>
                </div>
                
                <div class="favorite-info">
                  <h4 class="favorite-title">{{ favorite.target_info?.name || '未知' }}</h4>
                  <p v-if="favorite.favorite_type === 'school'" class="favorite-desc">
                    {{ favorite.target_info?.province || '' }} {{ favorite.target_info?.city || '' }}
                  </p>
                  <p v-else class="favorite-desc">
                    专业代码：{{ favorite.target_info?.code || '' }}
                  </p>
                  <p class="favorite-time">收藏时间：{{ formatTime(favorite.created_at) }}</p>
                </div>
                
                <div class="favorite-actions">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="viewFavorite(favorite)"
                  >
                    查看详情
                  </el-button>
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="removeFavoriteItem(favorite)"
                  >
                    取消收藏
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'
import { getFavorites, removeFavorite } from '../api/favorite'
import Header from '../components/Header.vue'

const router = useRouter()
const profileFormRef = ref()
const passwordFormRef = ref()

// 用户登录状态
const isLoggedIn = ref(false)
const userInfo = ref(null)
const miniSearch = ref('')

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

// 导航方法
const goToHome = () => {
  router.push('/')
}

const handleSearch = () => {
  if (miniSearch.value.trim()) {
    // 这里可以添加搜索逻辑
    console.log('搜索:', miniSearch.value)
  }
}

const handleLogin = () => {
  router.push('/login')
}

const handleRegister = () => {
  router.push('/register')
}

const handleLogout = () => {
  console.log('退出登录')
  // 清除本地存储的token
  localStorage.removeItem('userToken')
  localStorage.removeItem('userInfo')
  
  // 更新登录状态
  isLoggedIn.value = false
  userInfo.value = null
  
  // 跳转到首页
  router.push('/')
}

const profileLoading = ref(false)
const passwordLoading = ref(false)

const profileForm = reactive({
  username: '',
  nickname: '',
  email: '',
  phone: '',
  register_time: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 收藏相关数据
const activeFavoriteTab = ref('all')
const favoritesList = ref([])
const favoritesLoading = ref(false)

// 计算属性：过滤显示的收藏列表
const filteredFavorites = computed(() => {
  if (activeFavoriteTab.value === 'all') {
    return favoritesList.value
  }
  return favoritesList.value.filter(item => item.favorite_type === activeFavoriteTab.value)
})

const validateEmail = (rule, value, callback) => {
  if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    callback(new Error('请输入有效的邮箱地址'))
  } else {
    callback()
  }
}

const validatePhone = (rule, value, callback) => {
  if (value && !/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('请输入有效的手机号'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '昵称长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { validator: validateEmail, trigger: 'blur' }
  ],
  phone: [
    { validator: validatePhone, trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const loadProfile = async () => {
  try {
    const res = await request.get('/auth/profile')
    if (res.data.success) {
      Object.assign(profileForm, res.data.data)
    }
  } catch (error) {
    ElMessage.error('获取个人信息失败')
  }
}

// 加载收藏列表
const loadFavorites = async () => {
  favoritesLoading.value = true
  try {
    const res = await getFavorites()
    if (res.success) {
      favoritesList.value = res.data || []
    }
  } catch (error) {
    ElMessage.error('获取收藏列表失败')
    favoritesList.value = []
  } finally {
    favoritesLoading.value = false
  }
}

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return ''
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN')
}

// 查看收藏详情
const viewFavorite = (favorite) => {
  if (favorite.favorite_type === 'school') {
    router.push(`/school/${favorite.target_id}`)
  } else {
    router.push(`/major/${favorite.target_id}`)
  }
}

// 取消收藏
const removeFavoriteItem = async (favorite) => {
  try {
    await ElMessageBox.confirm('确定要取消收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const res = await removeFavorite({
      favorite_type: favorite.favorite_type,
      target_id: favorite.target_id
    })
    
    if (res.success) {
      ElMessage.success('取消收藏成功')
      // 重新加载收藏列表
      await loadFavorites()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消收藏失败')
    }
  }
}

const updateProfile = async () => {
  if (!profileFormRef.value) return
  
  const valid = await profileFormRef.value.validate()
  if (!valid) return
  
  profileLoading.value = true
  try {
    const res = await request.put('/auth/profile', profileForm)
    
    if (res.data.success) {
      ElMessage.success('个人信息更新成功')
      
      // 更新本地存储的用户信息
      const userInfo = localStorage.getItem('userInfo')
      if (userInfo) {
        const parsedInfo = JSON.parse(userInfo)
        parsedInfo.nickname = profileForm.nickname
        parsedInfo.email = profileForm.email
        parsedInfo.phone = profileForm.phone
        localStorage.setItem('userInfo', JSON.stringify(parsedInfo))
        
        // 触发Header组件更新
        window.dispatchEvent(new Event('storage'))
      }
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '更新失败')
  } finally {
    profileLoading.value = false
  }
}

const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  const valid = await passwordFormRef.value.validate()
  if (!valid) return
  
  passwordLoading.value = true
  try {
    const res = await request.put('/auth/change-password', {
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    
    if (res.data.success) {
      ElMessage.success('密码修改成功')
      
      // 清空表单
      passwordFormRef.value.resetFields()
      
      // 提示用户重新登录
      await ElMessageBox.confirm('密码修改成功，请重新登录', '提示', {
        confirmButtonText: '重新登录',
        cancelButtonText: '稍后',
        type: 'success'
      })
      
      // 清除本地存储
      localStorage.removeItem('userToken')
      localStorage.removeItem('userInfo')
      router.push('/login')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '密码修改失败')
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => {
  // 检查登录状态
  checkLoginStatus()
  
  // 如果没有登录，跳转到登录页面
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  loadProfile()
  loadFavorites()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.profile-container {
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
  gap: 8px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s;
  color: #666;
  font-size: 14px;
}

.dropdown-item:hover {
  background: #f5f5f5;
  color: #1a1a1a;
}

.dropdown-item i {
  width: 16px;
  text-align: center;
}

.profile-header {
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  color: white;
  padding: 100px 0 100px;
  text-align: center;
  margin-bottom: 0;
  position: relative;
  overflow: hidden;
}

.profile-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -15%;
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.profile-header h2 {
  color: white;
  font-size: 42px;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.profile-content {
  max-width: 1000px;
  margin: -60px auto 0;
  padding: 0 20px 80px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  position: relative;
  z-index: 10;
}

.profile-card,
.password-card,
.favorite-card {
  width: 100%;
  border: none;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(30, 136, 229, 0.12);
  transition: all 0.4s ease;
  background: white;
  border: 1px solid #e3f2fd;
  overflow: hidden;
}

.profile-card:hover,
.password-card:hover,
.favorite-card:hover {
  box-shadow: 0 12px 32px rgba(30, 136, 229, 0.18);
  transform: translateY(-4px);
  border-color: #90caf9;
}

.card-header {
  font-size: 22px;
  font-weight: 700;
  color: #1565c0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 2px solid #e3f2fd;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-radius: 16px 16px 0 0;
  position: relative;
}

.card-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, #1e88e5, #1565c0);
}

.tab-buttons {
  display: flex;
  gap: 8px;
}

.tab-buttons .el-button {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.loading-container {
  padding: 40px 24px;
  text-align: center;
}

.empty-container {
  padding: 60px 24px;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  padding: 24px;
}

.favorite-item {
  border: 1px solid #e3f2fd;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  background: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(30, 136, 229, 0.08);
}

.favorite-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #1e88e5, #1565c0);
}

.favorite-item:hover {
  box-shadow: 0 8px 24px rgba(30, 136, 229, 0.15);
  border-color: #bbdefb;
  transform: translateY(-2px);
}

.favorite-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.favorite-type {
  flex-shrink: 0;
}

.favorite-info {
  flex: 1;
  min-width: 0;
}

.favorite-title {
  margin: 0 0 8px 0;
  color: #1a1a1a;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
}

.favorite-desc {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.favorite-time {
  margin: 0;
  color: #999;
  font-size: 12px;
  font-weight: 500;
}

.favorite-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  flex-direction: column;
}

.favorite-actions .el-button {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.favorite-actions .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 表单样式优化 */
.el-form {
  padding: 24px;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-form-item__label {
  font-weight: 500;
  color: #1a1a1a;
}

.el-input {
  border-radius: 8px;
}

.el-button {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

@media (max-width: 768px) {
  .profile-header {
    padding: 40px 0 30px;
  }
  
  .profile-header h2 {
    font-size: 24px;
  }
  
  .profile-content {
    margin-top: -30px;
    padding: 0 16px 30px;
    gap: 16px;
  }
  
  .favorites-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 16px;
  }
  
  .favorite-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .favorite-actions {
    flex-direction: row;
    width: 100%;
    justify-content: flex-end;
  }
  
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .tab-buttons {
    width: 100%;
    justify-content: center;
  }
}
</style>