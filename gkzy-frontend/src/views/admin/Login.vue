<template>
  <div class="login-container">
    <div class="login-box">
      <h2>管理员登录</h2>
      
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input 
            v-model="form.username" 
            placeholder="用户名/邮箱"
            size="large"
          />
        </el-form-item>
        
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码"
            size="large"
            show-password
          />
        </el-form-item>
        
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
          <router-link to="/admin/register">注册管理员</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../../utils/request'

const router = useRouter()
const loading = ref(false)

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
    const res = await request.post('/admin/login', form.value)
    
    if (res.data.success) {
      localStorage.setItem('adminToken', res.data.data.token)
      localStorage.setItem('adminInfo', JSON.stringify(res.data.data.admin))
      ElMessage.success('登录成功')
      router.push('/admin/dashboard')
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.login-box h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.login-btn {
  width: 100%;
  margin-top: 20px;
}

.links {
  margin-top: 20px;
  text-align: center;
}

.links a {
  color: #409eff;
  text-decoration: none;
}
</style>