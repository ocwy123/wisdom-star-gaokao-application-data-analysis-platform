<template>
  <div class="admin-profile">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" disabled />
        </el-form-item>
        
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        
        <el-form-item label="真实姓名">
          <el-input v-model="form.real_name" />
        </el-form-item>
        
        <el-form-item label="角色">
          <el-input v-model="form.role" disabled />
        </el-form-item>
        
        <el-form-item label="创建时间">
          <el-input v-model="form.created_at" disabled />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleUpdate" :loading="updating">
            更新信息
          </el-button>
          <el-button @click="openChangePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 修改密码对话框 -->
    <el-dialog v-model="pwdDialogVisible" title="修改密码" width="400px">
      <el-form :model="pwdForm" label-width="100px" :rules="pwdRules" ref="pwdFormRef">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword" :loading="changing">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../../utils/request'

export default {
  name: 'AdminProfile',
  setup() {
    const form = ref({
      username: '',
      email: '',
      real_name: '',
      role: '',
      created_at: ''
    })
    
    const updating = ref(false)
    const pwdDialogVisible = ref(false)
    const changing = ref(false)
    const pwdFormRef = ref(null)
    
    const pwdForm = reactive({
      old_password: '',
      new_password: '',
      confirm_password: ''
    })
    
    const validateNewPass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入新密码'))
      } else if (value.length < 6) {
        callback(new Error('密码长度不能小于6位'))
      } else {
        if (pwdForm.confirm_password !== '') {
          pwdFormRef.value?.validateField('confirm_password')
        }
        callback()
      }
    }
    
    const validateConfirmPass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== pwdForm.new_password) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }
    
    const pwdRules = {
      old_password: [
        { required: true, message: '请输入原密码', trigger: 'blur' }
      ],
      new_password: [
        { validator: validateNewPass, trigger: 'blur' }
      ],
      confirm_password: [
        { validator: validateConfirmPass, trigger: 'blur' }
      ]
    }
    
    // 获取个人信息
    const fetchProfile = async () => {
      try {
        const res = await request.get('/admin/profile')
        if (res.data.success) {
          form.value = res.data.data
        }
      } catch (error) {
        ElMessage.error('获取个人信息失败')
      }
    }
    
    // 更新信息
    const handleUpdate = async () => {
      updating.value = true
      try {
        const res = await request.put('/admin/profile', {
          email: form.value.email,
          real_name: form.value.real_name
        })
        
        if (res.data.success) {
          ElMessage.success('更新成功')
          // 更新本地存储
          const adminInfo = JSON.parse(localStorage.getItem('adminInfo') || '{}')
          adminInfo.email = form.value.email
          adminInfo.real_name = form.value.real_name
          localStorage.setItem('adminInfo', JSON.stringify(adminInfo))
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '更新失败')
      } finally {
        updating.value = false
      }
    }
    
    // 打开修改密码对话框
    const openChangePassword = () => {
      pwdForm.old_password = ''
      pwdForm.new_password = ''
      pwdForm.confirm_password = ''
      pwdDialogVisible.value = true
    }
    
    // 修改密码
    const handleChangePassword = async () => {
      if (!pwdFormRef.value) return
      
      try {
        await pwdFormRef.value.validate()
        
        changing.value = true
        const res = await request.put('/admin/change-password', {
          old_password: pwdForm.old_password,
          new_password: pwdForm.new_password
        })
        
        if (res.data.success) {
          ElMessage.success('密码修改成功')
          pwdDialogVisible.value = false
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '修改失败')
      } finally {
        changing.value = false
      }
    }
    
    onMounted(() => {
      fetchProfile()
    })
    
    return {
      form,
      updating,
      pwdDialogVisible,
      pwdForm,
      pwdRules,
      pwdFormRef,
      changing,
      handleUpdate,
      openChangePassword,
      handleChangePassword
    }
  }
}
</script>

<style scoped>
.admin-profile {
  padding: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}
</style>