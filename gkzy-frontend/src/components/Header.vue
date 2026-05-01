<template>
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
          <router-link to="/recommendation" class="nav-item">志愿推荐</router-link>
          <router-link to="/compare" class="nav-item">多维对比</router-link>
          <!-- <router-link to="/analysis/deep-search" class="nav-item">深度检索</router-link> -->
        </nav>
      </div>
      <div class="header-right">
        <button v-if="!isLoggedIn" class="btn btn-text" @click="handleLogin">登录</button>
        <!-- <button class="btn btn-primary" @click="handleRegister">注册</button> -->

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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

// 用户登录状态
const isLoggedIn = ref(false)
const userInfo = ref(null)

// 检查登录状态
const checkLoginStatus = () => {
  const token = localStorage.getItem('userToken')
  const info = localStorage.getItem('userInfo')
  
  isLoggedIn.value = !!token
  if (info) {
    try {
      userInfo.value = JSON.parse(info)
    } catch (e) {
      userInfo.value = null
    }
  } else if (token) {
    // 兼容旧 token 存储方式（解析 token 获取用户名）
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      userInfo.value = { username: payload.username, role: payload.role }
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    } catch (error) {
      console.error('解析token失败:', error)
    }
  } else {
    userInfo.value = null
  }
}

// 滚动到顶部
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 登录
const handleLogin = () => {
  router.push('/login')
}

// 注册
const handleRegister = () => {
  router.push('/register')
}

// 个人中心
const goToProfile = () => {
  router.push('/profile')
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 清除本地存储
    localStorage.removeItem('userToken')
    localStorage.removeItem('userInfo')
    
    // 更新状态
    isLoggedIn.value = false
    userInfo.value = null
    
    ElMessage.success('退出登录成功')
    router.push('/')
  } catch (error) {
    // 用户取消操作
  }
}

// 监听 storage 变化（多标签页同步）
const storageListener = () => {
  checkLoginStatus()
}

onMounted(() => {
  checkLoginStatus()
  window.addEventListener('storage', storageListener)
})

// 组件卸载时清理监听（可选，但组件通常不会被销毁）
</script>

<style scoped>
.header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header .container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
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
.nav-item.router-link-active {
  color: #1e88e5;
}

.nav-item.router-link-active::after {
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

/* 响应式设计（与 Dashboard 保持一致） */
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

  .btn {
    flex: 1;
    padding: 8px 14px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
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

  .btn {
    padding: 7px 13px;
    font-size: 13px;
  }
}
</style>