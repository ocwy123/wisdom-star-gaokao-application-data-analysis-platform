<template>
  <header class="app-header">
    <div class="logo">
      <router-link to="/">
        <img src="@/assets/logo.png" alt="高考志愿数据分析平台" />
        <span>高考志愿</span>
      </router-link>
    </div>

    <div class="search-box">
      <input
        type="text"
        v-model="keyword"
        placeholder="搜索高校、专业或政策"
        @keyup.enter="handleSearch"
      />
      <button @click="handleSearch">搜索</button>
    </div>

    <nav class="main-nav">
      <router-link to="/">首页</router-link>
      <router-link to="/schools">高校查询</router-link>
      <router-link to="/majors">专业查询</router-link>
      <router-link to="/volunteer">志愿填报</router-link>
    </nav>

    <div class="user-info">
      <template v-if="!isLoggedIn">
        <router-link to="/login">登录</router-link> |
        <router-link to="/register">注册</router-link>
      </template>
      <template v-else>
        <el-dropdown>
          <span class="user-dropdown">
            {{ username }}<el-icon><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="goToProfile">个人中心</el-dropdown-item>
              <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const keyword = ref('')
// 模拟登录状态，实际应从 store 或 localStorage 获取
const isLoggedIn = ref(false)
const username = ref('')

const handleSearch = () => {
  if (!keyword.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  // 跳转到全局搜索结果页（需实现）
  router.push({ path: '/search', query: { q: keyword.value } })
}

const goToProfile = () => {
  router.push('/profile')
}

const logout = () => {
  // 清除 token 等逻辑
  isLoggedIn.value = false
  router.push('/')
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 70px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.logo a {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #333;
}
.logo img {
  height: 40px;
  margin-right: 8px;
}
.logo span {
  font-size: 20px;
  font-weight: bold;
}
.search-box {
  display: flex;
  margin: 0 30px;
  flex: 1;
  max-width: 400px;
}
.search-box input {
  flex: 1;
  height: 36px;
  border: 1px solid #dcdfe6;
  border-right: none;
  border-radius: 18px 0 0 18px;
  padding: 0 15px;
  outline: none;
}
.search-box button {
  width: 60px;
  height: 36px;
  background-color: #409eff;
  border: 1px solid #409eff;
  border-radius: 0 18px 18px 0;
  color: white;
  cursor: pointer;
}
.main-nav {
  display: flex;
  gap: 20px;
  margin-right: 20px;
}
.main-nav a {
  text-decoration: none;
  color: #333;
  font-size: 16px;
}
.main-nav a.router-link-active {
  color: #409eff;
  font-weight: bold;
}
.user-info {
  margin-left: auto;
}
.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>