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
      router.push('/')
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
  min-height: 100vh;
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.login-container::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -5%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 8s ease-in-out infinite 2s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.login-box {
  width: 460px;
  padding: 48px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease-out;
  position: relative;
  z-index: 1;
}

.login-box:hover {
  box-shadow: 0 25px 70px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.logo-section {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  font-size: 42px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 12px 0;
  letter-spacing: 3px;
}

.slogan {
  font-size: 15px;
  color: #666;
  margin: 0;
  font-weight: 500;
}

.title {
  text-align: center;
  margin-bottom: 40px;
  color: #1a1a1a;
  font-size: 28px;
  font-weight: 700;
}

.login-form {
  width: 100%;
}

.form-input {
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 2px solid #e8e8e8;
}

.form-input:hover {
  border-color: #1e88e5;
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
}

.form-input:focus {
  border-color: #1e88e5;
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
}

.input-icon {
  color: #999;
  font-size: 18px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0 24px 0;
}

.remember-checkbox {
  color: #666;
  font-size: 14px;
}

.forgot-password {
  color: #1e88e5;
  font-size: 14px;
  text-decoration: none;
  transition: color 0.3s ease;
  font-weight: 500;
}

.forgot-password:hover {
  color: #1565c0;
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  margin-top: 12px;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(30, 136, 229, 0.2);
}

.login-btn:hover {
  background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(30, 136, 229, 0.3);
}

.links {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.register-link {
  color: #1e88e5;
  font-weight: 600;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.3s ease;
}

.register-link:hover {
  color: #1565c0;
  text-decoration: underline;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
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
    padding: 36px 28px;
  }
  
  .logo {
    font-size: 36px;
  }
  
  .title {
    font-size: 24px;
  }
  
  .social-login {
    flex-direction: column;
  }
}
</style>