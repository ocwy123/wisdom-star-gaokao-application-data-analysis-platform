<template>
  <div class="register-container">
    <div class="register-box">
      <div class="logo-section">
        <h1 class="logo">GKZY</h1>
        <p class="slogan">高考志愿填报系统</p>
      </div>
      
      <h2 class="title">用户注册</h2>
      
      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleRegister" class="register-form">
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="用户名"
            size="large"
            class="form-input"
          >
            <template #prefix>
              <el-icon class="input-icon"><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="nickname">
          <el-input 
            v-model="form.nickname" 
            placeholder="昵称"
            size="large"
            class="form-input"
          >
            <template #prefix>
              <el-icon class="input-icon"><Avatar /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
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
        
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="form.confirmPassword" 
            type="password" 
            placeholder="确认密码"
            size="large"
            show-password
            class="form-input"
          >
            <template #prefix>
              <el-icon class="input-icon"><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="email">
          <el-input 
            v-model="form.email" 
            placeholder="邮箱（可选）"
            size="large"
            class="form-input"
          >
            <template #prefix>
              <el-icon class="input-icon"><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="phone">
          <el-input 
            v-model="form.phone" 
            placeholder="手机号（可选）"
            size="large"
            class="form-input"
          >
            <template #prefix>
              <el-icon class="input-icon"><Phone /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="agreedToTerms" class="terms-checkbox">
            我已阅读并同意 <a href="#" class="terms-link">用户协议</a> 和 <a href="#" class="terms-link">隐私政策</a>
          </el-checkbox>
        </el-form-item>
        
        <el-button 
          type="primary" 
          :loading="loading"
          class="register-btn"
          size="large"
          @click="handleRegister"
        >
          注册
        </el-button>
        
        <div class="links">
          <span>已有账号？</span>
          <router-link to="/login" class="login-link">立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Phone, Avatar } from '@element-plus/icons-vue'
import request from '../utils/request'

const router = useRouter()
const loading = ref(false)
const formRef = ref()
const agreedToTerms = ref(false)

const form = reactive({
  username: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  email: '',
  phone: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

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

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '昵称长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  email: [
    { validator: validateEmail, trigger: 'blur' }
  ],
  phone: [
    { validator: validatePhone, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!formRef.value) return
  
  if (!agreedToTerms.value) {
    ElMessage.warning('请阅读并同意用户协议和隐私政策')
    return
  }
  
  const valid = await formRef.value.validate()
  if (!valid) return
  
  loading.value = true
  try {
    const { confirmPassword, ...submitData } = form
    const res = await request.post('/auth/register', submitData)
    
    if (res.data.success) {
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  position: relative;
  overflow: hidden;
}

.register-container::before {
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

.register-container::after {
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

.register-box {
  width: 480px;
  padding: 48px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease-out;
  position: relative;
  z-index: 1;
}

.register-box:hover {
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

.register-form {
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

.terms-checkbox {
  color: #666;
  font-size: 14px;
  margin: 20px 0;
}

.terms-link {
  color: #1e88e5;
  text-decoration: none;
  transition: color 0.3s ease;
  font-weight: 500;
}

.terms-link:hover {
  color: #1565c0;
  text-decoration: underline;
}

.register-btn {
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

.register-btn:hover {
  background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(30, 136, 229, 0.3);
}

.links {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.login-link {
  color: #1e88e5;
  font-weight: 600;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.3s ease;
}

.login-link:hover {
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
  .register-box {
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
}
</style>