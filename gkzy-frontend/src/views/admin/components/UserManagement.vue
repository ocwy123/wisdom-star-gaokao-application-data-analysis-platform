<template>
  <div class="user-management">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索用户名/昵称/邮箱"
        style="width: 300px"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
      
      <el-button type="primary" @click="refreshList" style="margin-left: 10px;">
        刷新
      </el-button>
    </div>

    <!-- 用户列表 -->
    <el-table :data="users" border stripe v-loading="loading" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="nickname" label="昵称" width="120" />
      <el-table-column prop="email" label="邮箱" width="180" />
      <el-table-column prop="phone" label="手机号" width="120" />
      <el-table-column prop="role" label="角色" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 0 ? 'success' : 'danger'">
            {{ row.status === 0 ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="register_time" label="注册时间" width="160" />
      <el-table-column label="操作" fixed="right" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="viewUser(row)">查看</el-button>
          <el-button 
            size="small" 
            :type="row.status === 0 ? 'warning' : 'success'"
            @click="toggleStatus(row)"
          >
            {{ row.status === 0 ? '禁用' : '启用' }}
          </el-button>
          <el-button size="small" type="danger" @click="deleteUser(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 查看用户详情对话框 -->
    <el-dialog v-model="dialogVisible" title="用户详情" width="500px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="ID">{{ currentUser.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
        <el-descriptions-item label="昵称">{{ currentUser.nickname }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ currentUser.email }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ currentUser.phone }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ currentUser.role }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentUser.status === 0 ? 'success' : 'danger'">
            {{ currentUser.status === 0 ? '正常' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ currentUser.register_time }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../../../utils/request'

export default {
  name: 'UserManagement',
  setup() {
    const users = ref([])
    const loading = ref(false)
    const searchKeyword = ref('')
    const dialogVisible = ref(false)
    const currentUser = ref({})

    // 获取用户列表
    const fetchUsers = async () => {
      loading.value = true
      try {
        const res = await request.get('/admin/users')
        if (res.data.success) {
          users.value = res.data.data
        }
      } catch (error) {
        ElMessage.error('获取用户列表失败')
      } finally {
        loading.value = false
      }
    }

    // 搜索
    const handleSearch = async () => {
      if (!searchKeyword.value) {
        fetchUsers()
        return
      }
      
      loading.value = true
      try {
        const res = await request.get(`/admin/users/search?keyword=${searchKeyword.value}`)
        if (res.data.success) {
          users.value = res.data.data
        }
      } catch (error) {
        ElMessage.error('搜索失败')
      } finally {
        loading.value = false
      }
    }

    // 刷新列表
    const refreshList = () => {
      searchKeyword.value = ''
      fetchUsers()
    }

    // 查看用户
    const viewUser = (row) => {
      currentUser.value = row
      dialogVisible.value = true
    }

    // 切换状态
    const toggleStatus = async (row) => {
      const newStatus = row.status === 0 ? 1 : 0
      const action = newStatus === 0 ? '启用' : '禁用'
      
      try {
        ElMessageBox.confirm(`确定要${action}用户 ${row.username} 吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const res = await request.put(`/admin/users/${row.id}`, {
          status: newStatus
        })
        
        if (res.data.success) {
          ElMessage.success(`${action}成功`)
          fetchUsers()
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.response?.data?.message || `${action}失败`)
        }
      }
    }

    // 删除用户
    const deleteUser = async (row) => {
      try {
        await ElMessageBox.confirm(`确定要删除用户 ${row.username} 吗？`, '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'error'
        })
        
        const res = await request.delete(`/admin/users/${row.id}`)
        
        if (res.data.success) {
          ElMessage.success('删除成功')
          fetchUsers()
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.response?.data?.message || '删除失败')
        }
      }
    }

    onMounted(() => {
      fetchUsers()
    })

    return {
      users,
      loading,
      searchKeyword,
      dialogVisible,
      currentUser,
      fetchUsers,
      handleSearch,
      refreshList,
      viewUser,
      toggleStatus,
      deleteUser
    }
  }
}
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}
</style>