<template>
  <div class="database-status">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据库状态</span>
          <el-button type="primary" size="small" @click="fetchStatus" :loading="loading">
            刷新
          </el-button>
        </div>
      </template>
      
      <div v-if="status" class="status-content">
        <el-alert
          :title="status.message"
          :type="status.success ? 'success' : 'error'"
          :closable="false"
          style="margin-bottom: 20px;"
        />
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="数据库">
            {{ status.data?.database }}
          </el-descriptions-item>
          <el-descriptions-item label="管理员表存在">
            <el-tag :type="status.data?.admin_table_exists ? 'success' : 'danger'">
              {{ status.data?.admin_table_exists ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="用户表存在">
            <el-tag :type="status.data?.user_table_exists ? 'success' : 'danger'">
              {{ status.data?.user_table_exists ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总表数">
            {{ status.data?.tables?.length || 0 }}
          </el-descriptions-item>
        </el-descriptions>       
        <el-divider v-if="status.data?.admin_table_fields?.length">管理员表字段</el-divider>
        
        <el-table 
          v-if="status.data?.admin_table_fields?.length" 
          :data="status.data.admin_table_fields" 
          border 
          stripe 
          style="width: 100%; margin-top: 10px;"
        >
          <el-table-column prop="name" label="字段名" />
          <el-table-column prop="type" label="类型" />
          <el-table-column prop="nullable" label="可为空" width="80">
            <template #default="{ row }">
              {{ row.nullable ? '是' : '否' }}
            </template>
          </el-table-column>
          <el-table-column prop="primary_key" label="主键" width="80">
            <template #default="{ row }">
              {{ row.primary_key ? '是' : '否' }}
            </template>
          </el-table-column>
        </el-table>
        
        <el-divider v-if="status.data?.user_table_fields?.length">用户表字段</el-divider>
        
        <el-table 
          v-if="status.data?.user_table_fields?.length" 
          :data="status.data.user_table_fields" 
          border 
          stripe 
          style="width: 100%; margin-top: 10px;"
        >
          <el-table-column prop="name" label="字段名" />
          <el-table-column prop="type" label="类型" />
          <el-table-column prop="nullable" label="可为空" width="80">
            <template #default="{ row }">
              {{ row.nullable ? '是' : '否' }}
            </template>
          </el-table-column>
          <el-table-column prop="primary_key" label="主键" width="80">
            <template #default="{ row }">
              {{ row.primary_key ? '是' : '否' }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../utils/request'

export default {
  name: 'DatabaseStatus',
  setup() {
    const loading = ref(false)
    const status = ref(null)

    const fetchStatus = async () => {
      loading.value = true
      try {
        const res = await request.get('/admin/check-database')
        if (res.data.success) {
          status.value = res.data
        } else {
          ElMessage.error('获取数据库状态失败')
        }
      } catch (error) {
        ElMessage.error('获取数据库状态失败')
      } finally {
        loading.value = false
      }
    }

    const tableList = computed(() => {
      if (!status.value?.data?.record_counts) return []
      return Object.entries(status.value.data.record_counts).map(([name, count]) => ({
        name,
        count
      }))
    })

    onMounted(() => {
      fetchStatus()
    })

    return {
      loading,
      status,
      tableList,
      fetchStatus
    }
  }
}
</script>

<style scoped>
.database-status {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.status-content {
  padding: 10px;
}
</style>