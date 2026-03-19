<template>
  <div class="register-container">
    <div class="register-box">
      <h2>管理员注册</h2>
      
      <el-form :model="form" @submit.prevent="handleRegister">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" />
        </el-form-item>
        
        <el-form-item>
          <el-input v-model="form.email" placeholder="邮箱" />
        </el-form-item>
        
        <el-form-item>
          <el-input v-model="form.real_name" placeholder="真实姓名" />
        </el-form-item>
        
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码（至少6位）"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-input 
            v-model="form.confirm_password" 
            type="password" 
            placeholder="确认密码"
            show-password
          />
        </el-form-item>
        
        <el-button 
          type="primary" 
          :loading="loading"
          class="register-btn"
          @click="handleRegister"
        >
          注册
        </el-button>
        
        <div class="links">
          <router-link to="/admin/login">返回登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../../../utils/request'

const router = useRouter()
const loading = ref(false)

const form = ref({
  username: '',
  email: '',
  real_name: '',
  password: '',
  confirm_password: ''
})

const handleRegister = async () => {
  if (!form.value.username || !form.value.email || !form.value.password) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  if (form.value.password.length < 6) {
    ElMessage.warning('密码至少6位')
    return
  }
  
  if (form.value.password !== form.value.confirm_password) {
    ElMessage.warning('两次密码不一致')
    return
  }
  
  loading.value = true
  try {
    const res = await request.post('/admin/register', {
      username: form.value.username,
      email: form.value.email,
      real_name: form.value.real_name,
      password: form.value.password
    })
    
    if (res.data.success) {
      localStorage.setItem('adminToken', res.data.data.token)
      localStorage.setItem('adminInfo', JSON.stringify(res.data.data.admin))
      ElMessage.success('注册成功')
      router.push('/admin/dashboard')
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-box {
  width: 450px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.register-box h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.register-btn {
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