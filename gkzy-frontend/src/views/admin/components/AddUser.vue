<template>
  <div class="add-user">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>添加新用户</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码（至少6位）"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="form.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色">
            <el-option label="普通用户" value="普通用户" />
            <el-option label="管理员" value="管理员" />
            <el-option label="VIP用户" value="VIP用户" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="0">正常</el-radio>
            <el-radio :label="1">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            提交
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../../utils/request'

export default {
  name: 'AddUser',
  emits: ['success'],
  setup(props, { emit }) {
    const formRef = ref(null)
    const submitting = ref(false)
    
    const form = reactive({
      username: '',
      nickname: '',
      email: '',
      phone: '',
      password: '',
      confirmPassword: '',
      role: '普通用户',
      status: 0
    })
    
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else if (value.length < 6) {
        callback(new Error('密码长度不能小于6位'))
      } else {
        if (form.confirmPassword !== '') {
          formRef.value.validateField('confirmPassword')
        }
        callback()
      }
    }
    
    const validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== form.password) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }
    
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '长度在3到20个字符', trigger: 'blur' }
      ],
      nickname: [
        { required: true, message: '请输入昵称', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      password: [
        { validator: validatePass, trigger: 'blur' }
      ],
      confirmPassword: [
        { validator: validatePass2, trigger: 'blur' }
      ]
    }
    
    const handleSubmit = async () => {
      if (!formRef.value) return
      
      try {
        await formRef.value.validate()
        
        submitting.value = true
        
        const res = await request.post('/admin/users', {
          username: form.username,
          nickname: form.nickname,
          email: form.email,
          phone: form.phone,
          password: form.password,
          role: form.role,
          status: form.status
        })
        
        if (res.data.success) {
          ElMessage.success('用户添加成功')
          resetForm()
          emit('success')
        }
      } catch (error) {
        console.error('添加用户失败:', error)
        ElMessage.error(error.response?.data?.message || '添加失败')
      } finally {
        submitting.value = false
      }
    }
    
    const resetForm = () => {
      formRef.value?.resetFields()
    }
    
    return {
      formRef,
      form,
      rules,
      submitting,
      handleSubmit,
      resetForm
    }
  }
}
</script>

<style scoped>
.add-user {
  padding: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}
</style>