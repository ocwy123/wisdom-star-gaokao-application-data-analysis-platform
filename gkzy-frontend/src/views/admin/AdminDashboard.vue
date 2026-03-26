<template>
  <div class="admin-dashboard">
    <!-- 头部 -->
    <div class="header">
      <h2>管理员系统</h2>
      <div class="user-info">
        <span>欢迎，{{ adminInfo.real_name || adminInfo.username }}</span>
        <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
      </div>
    </div>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="main-tabs" type="border-card">
      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="users">
        <UserManagement ref="userManagementRef" />
      </el-tab-pane>
      
      <!-- 系统配置 -->
      <el-tab-pane label="系统配置" name="config">
        <SystemConfig />
      </el-tab-pane>
      
      <!-- 添加用户 -->
      <el-tab-pane label="添加用户" name="add">
        <AddUser @success="onUserAdded" />
      </el-tab-pane>
      
      <!-- 个人信息 -->
      <el-tab-pane label="个人信息" name="profile">
        <AdminProfile />
      </el-tab-pane>
      
      <!-- 数据导入 -->
      <el-tab-pane label="数据导入" name="import">
        <DataImport />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import UserManagement from './components/UserManagement.vue'
import SystemConfig from './components/SystemConfig.vue'
import AddUser from './components/AddUser.vue'
import AdminProfile from './components/AdminProfile.vue'
import DataImport from './components/DataImport.vue'

export default {
  name: 'AdminDashboard',
  components: {
    UserManagement,
    SystemConfig,
    AddUser,
    AdminProfile,
    DataImport
  },
  setup() {
    const router = useRouter()
    const activeTab = ref('users')  // 默认选中用户管理
    const adminInfo = ref(JSON.parse(localStorage.getItem('adminInfo') || '{}'))
    const userManagementRef = ref(null)

    // 退出登录
    const handleLogout = () => {
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }).then(() => {
        localStorage.removeItem('adminToken')
        localStorage.removeItem('adminInfo')
        router.push('/admin/login')
        ElMessage.success('已退出登录')
      }).catch(() => {})
    }

    // 添加用户成功后的回调
    const onUserAdded = () => {
      activeTab.value = 'users'  // 切换到用户管理标签
      if (userManagementRef.value) {
        userManagementRef.value.fetchUsers()  // 刷新用户列表
      }
    }

    return {
      activeTab,
      adminInfo,
      userManagementRef,
      handleLogout,
      onUserAdded
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  background-color: white;
  padding: 20px 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info span {
  font-size: 16px;
  color: #666;
}

.main-tabs {
  margin: 0 30px;
  background-color: white;
  border-radius: 8px;
  min-height: calc(100vh - 140px);
}

/* 标签页样式 */
:deep(.el-tabs__header) {
  margin-bottom: 20px;
  padding: 0 20px;
  padding-top: 10px;
}

:deep(.el-tabs__item) {
  font-size: 16px;
  padding: 0 20px;
}

:deep(.el-tabs__content) {
  padding: 20px;
}
</style>