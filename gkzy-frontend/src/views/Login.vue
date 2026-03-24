<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo-section">
        <h1 class="logo">GKZY</h1>
        <p class="slogan">高考志愿填报系统</p>
      </div>
      
      <h2 class="title">用户登录</h2>
      
      <el-form :model="form" @submit.prevent="handleLogin" class="login-form">
        <el-form-item>
          <el-input 
            v-model="form.username" 
            placeholder="用户名/邮箱/手机号"
            size="large"
            class="form-input"
          >
            <template #prefix>
              <el-icon class="input-icon"><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码"
            size="large"
            show-password
            class="form-input"
          >
            <template #prefix>
              <el-icon class="input-icon"><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <div class="form-options">
          <el-checkbox v-model="rememberMe" class="remember-checkbox">记住我</el-checkbox>
          <router-link to="#" class="forgot-password">忘记密码？</router-link>
        </div>
        
        <el-button 
          type="primary" 
          :loading="loading"
          class="login-btn"
          size="large"
          @click="handleLogin"
        >
          登录
        </el-button>
        
        <div class="divider">
          <span>或</span>
        </div>
        
        <div class="social-login">
          <el-button class="social-btn" type="default" size="large">
            <el-icon class="social-icon"><Monitor /></el-icon>
            微信登录
          </el-button>
          <el-button class="social-btn" type="default" size="large">
            <el-icon class="social-icon"><Phone /></el-icon>
            手机号登录
          </el-button>
        </div>
        
        <div class="links">
          <span>还没有账号？</span>
          <router-link to="/register" class="register-link">立即注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Monitor, Phone } from '@element-plus/icons-vue'
import request from '../utils/request'

const router = useRouter()
const loading = ref(false)
const rememberMe = ref(false)

const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  
  loading.value = true
  try {
    const res = await request.post('/auth/login', form.value)
    
    if (res.data.success) {
      localStorage.setItem('userToken', res.data.data.token)
      localStorage.setItem('userInfo', JSON.stringify(res.data.data.user))
      if (rememberMe.value) {
        localStorage.setItem('rememberedUser', form.value.username)
      } else {
        localStorage.removeItem('rememberedUser')
      }
      ElMessage.success('登录成功')
      router.push('/dashboard')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, var(--accent) 0%, #764ba2 100%);
  transition: background 0.3s ease;
}

.login-box {
  width: 420px;
  padding: 48px;
  background: var(--bg);
  border-radius: 12px;
  box-shadow: var(--shadow);
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease-out;
}

.login-box:hover {
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.logo-section {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 32px;
  font-weight: 700;
  color: var(--accent);
  margin: 0 0 8px 0;
  letter-spacing: 2px;
}

.slogan {
  font-size: 14px;
  color: var(--text);
  margin: 0;
}

.title {
  text-align: center;
  margin-bottom: 32px;
  color: var(--text-h);
  font-size: 24px;
  font-weight: 600;
}

.login-form {
  width: 100%;
}

.form-input {
  border-radius: 8px;
  transition: all 0.3s ease;
  border: 1px solid var(--border);
}

.form-input:hover {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px var(--accent-bg);
}

.form-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px var(--accent-bg);
}

.input-icon {
  color: var(--text);
  font-size: 18px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0 24px 0;
}

.remember-checkbox {
  color: var(--text);
  font-size: 14px;
}

.forgot-password {
  color: var(--accent);
  font-size: 14px;
  text-decoration: none;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: var(--accent);
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  margin-top: 8px;
  height: 48px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  background: var(--accent);
  border: none;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: #9631e8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(170, 59, 255, 0.3);
}

.divider {
  position: relative;
  text-align: center;
  margin: 32px 0;
  color: var(--text);
  font-size: 14px;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--border);
  z-index: 0;
}

.divider span {
  position: relative;
  background: var(--bg);
  padding: 0 16px;
  z-index: 1;
}

.social-login {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
}

.social-btn {
  flex: 1;
  height: 44px;
  border-radius: 8px;
  border: 1px solid var(--border);
  transition: all 0.3s ease;
}

.social-btn:hover {
  border-color: var(--accent);
  background: var(--accent-bg);
  transform: translateY(-1px);
}

.social-icon {
  margin-right: 8px;
  font-size: 18px;
}

.links {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
  color: var(--text);
}

.register-link {
  color: var(--accent);
  font-weight: 600;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.3s ease;
}

.register-link:hover {
  color: #9631e8;
  text-decoration: underline;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-box {
    width: 90%;
    max-width: 400px;
    padding: 32px;
  }
  
  .social-login {
    flex-direction: column;
  }
}
</style>