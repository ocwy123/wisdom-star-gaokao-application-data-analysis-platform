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
  height: 100vh;
  background: linear-gradient(135deg, var(--accent) 0%, #764ba2 100%);
  transition: background 0.3s ease;
}

.register-box {
  width: 440px;
  padding: 48px;
  background: var(--bg);
  border-radius: 12px;
  box-shadow: var(--shadow);
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease-out;
  max-height: 85vh;
  overflow-y: auto;
}

.register-box:hover {
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

.register-form {
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

.terms-checkbox {
  color: var(--text);
  font-size: 14px;
  margin: 16px 0;
}

.terms-link {
  color: var(--accent);
  text-decoration: none;
  transition: color 0.3s ease;
}

.terms-link:hover {
  color: #9631e8;
  text-decoration: underline;
}

.register-btn {
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

.register-btn:hover {
  background: #9631e8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(170, 59, 255, 0.3);
}

.links {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: var(--text);
}

.login-link {
  color: var(--accent);
  font-weight: 600;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.3s ease;
}

.login-link:hover {
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
  .register-box {
    width: 90%;
    max-width: 400px;
    padding: 32px;
  }
}

/* 滚动条样式 */
.register-box::-webkit-scrollbar {
  width: 6px;
}

.register-box::-webkit-scrollbar-track {
  background: var(--border);
  border-radius: 3px;
}

.register-box::-webkit-scrollbar-thumb {
  background: var(--text);
  border-radius: 3px;
}

.register-box::-webkit-scrollbar-thumb:hover {
  background: var(--accent);
}
</style>