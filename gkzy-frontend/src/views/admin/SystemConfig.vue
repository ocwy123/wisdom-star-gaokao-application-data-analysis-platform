<template>
  <div class="system-config">
    <el-tabs v-model="activeConfigTab" type="border-card">
      <!-- 数据源配置 -->
      <el-tab-pane label="数据源配置" name="datasource">
        <el-form :model="config.datasource" label-width="150px" ref="datasourceForm">
          <el-form-item label="API地址" prop="api_url" :rules="[{ required: true, message: '请输入API地址' }]">
            <el-input v-model="config.datasource.api_url" placeholder="http://api.example.com" />
          </el-form-item>
          
          <el-form-item label="数据库主机" prop="db_host" :rules="[{ required: true, message: '请输入数据库主机' }]">
            <el-input v-model="config.datasource.db_host" placeholder="localhost" />
          </el-form-item>
          
          <el-form-item label="数据库端口" prop="db_port" :rules="[{ required: true, message: '请输入数据库端口' }]">
            <el-input-number v-model="config.datasource.db_port" :min="1" :max="65535" />
          </el-form-item>
          
          <el-form-item label="数据库名称" prop="db_name" :rules="[{ required: true, message: '请输入数据库名称' }]">
            <el-input v-model="config.datasource.db_name" placeholder="gkzy" />
          </el-form-item>
          
          <el-form-item label="数据库用户名" prop="db_user" :rules="[{ required: true, message: '请输入数据库用户名' }]">
            <el-input v-model="config.datasource.db_user" placeholder="root" />
          </el-form-item>
          
          <el-form-item label="数据库密码" prop="db_password">
            <el-input v-model="config.datasource.db_password" type="password" show-password />
          </el-form-item>
          
          <el-form-item label="爬虫数据源" prop="spider_source">
            <el-select v-model="config.datasource.spider_source" placeholder="请选择">
              <el-option label="内部爬虫" value="internal" />
              <el-option label="外部API" value="external" />
              <el-option label="文件导入" value="file" />
            </el-select>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- 缓存策略 -->
      <el-tab-pane label="缓存策略" name="cache">
        <el-form :model="config.cache" label-width="150px" ref="cacheForm">
          <el-form-item label="缓存开关">
            <el-switch v-model="config.cache.enabled" active-text="开启" inactive-text="关闭" />
          </el-form-item>
          
          <el-form-item label="缓存过期时间" prop="expire_time" :rules="[{ required: true, message: '请输入缓存过期时间' }]">
            <el-input-number v-model="config.cache.expire_time" :min="1" :max="86400" />
            <span class="unit">秒</span>
          </el-form-item>
          
          <el-form-item label="缓存容量" prop="capacity" :rules="[{ required: true, message: '请输入缓存容量' }]">
            <el-input-number v-model="config.cache.capacity" :min="1" :max="10000" />
            <span class="unit">MB</span>
          </el-form-item>
          
          <el-form-item label="缓存策略" prop="strategy">
            <el-radio-group v-model="config.cache.strategy">
              <el-radio label="LRU">LRU（最近最少使用）</el-radio>
              <el-radio label="LFU">LFU（最不经常使用）</el-radio>
              <el-radio label="FIFO">FIFO（先进先出）</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- 日志级别 -->
      <el-tab-pane label="日志级别" name="log">
        <el-form :model="config.log" label-width="150px" ref="logForm">
          <el-form-item label="日志级别" prop="level" :rules="[{ required: true, message: '请选择日志级别' }]">
            <el-select v-model="config.log.level" placeholder="请选择日志级别">
              <el-option label="DEBUG" value="DEBUG" />
              <el-option label="INFO" value="INFO" />
              <el-option label="WARNING" value="WARNING" />
              <el-option label="ERROR" value="ERROR" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="日志文件大小" prop="file_size" :rules="[{ required: true, message: '请输入日志文件大小' }]">
            <el-input-number v-model="config.log.file_size" :min="1" :max="1024" />
            <span class="unit">MB</span>
          </el-form-item>
          
          <el-form-item label="日志保留天数" prop="keep_days" :rules="[{ required: true, message: '请输入日志保留天数' }]">
            <el-input-number v-model="config.log.keep_days" :min="1" :max="365" />
            <span class="unit">天</span>
          </el-form-item>
          
          <el-form-item label="日志输出" prop="output">
            <el-checkbox-group v-model="config.log.output">
              <el-checkbox label="console">控制台</el-checkbox>
              <el-checkbox label="file">文件</el-checkbox>
              <el-checkbox label="database">数据库</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- 系统参数 -->
      <el-tab-pane label="系统参数" name="system">
        <el-form :model="config.system" label-width="150px" ref="systemForm">
          <el-form-item label="超时时间" prop="timeout" :rules="[{ required: true, message: '请输入超时时间' }]">
            <el-input-number v-model="config.system.timeout" :min="1" :max="300" />
            <span class="unit">秒</span>
          </el-form-item>
          
          <el-form-item label="最大并发用户数" prop="max_concurrent" :rules="[{ required: true, message: '请输入最大并发用户数' }]">
            <el-input-number v-model="config.system.max_concurrent" :min="1" :max="10000" />
            <span class="unit">人</span>
          </el-form-item>
          
          <el-form-item label="文件上传大小限制" prop="max_file_size" :rules="[{ required: true, message: '请输入文件上传大小限制' }]">
            <el-input-number v-model="config.system.max_file_size" :min="1" :max="1024" />
            <span class="unit">MB</span>
          </el-form-item>
          
          <el-form-item label="允许文件类型" prop="file_types">
            <el-select v-model="config.system.file_types" multiple placeholder="请选择">
              <el-option label="图片" value="image" />
              <el-option label="文档" value="document" />
              <el-option label="视频" value="video" />
              <el-option label="压缩包" value="archive" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="会话超时时间" prop="session_timeout" :rules="[{ required: true, message: '请输入会话超时时间' }]">
            <el-input-number v-model="config.system.session_timeout" :min="5" :max="1440" />
            <span class="unit">分钟</span>
          </el-form-item>
          
          <el-form-item label="密码重试次数" prop="password_retry" :rules="[{ required: true, message: '请输入密码重试次数' }]">
            <el-input-number v-model="config.system.password_retry" :min="1" :max="10" />
            <span class="unit">次</span>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button type="primary" @click="handleSave" :loading="saving">
        保存配置
      </el-button>
      <el-button @click="handleReset">重置</el-button>
      <el-button @click="fetchConfig">刷新</el-button>
    </div>
    
    <!-- 变更日志 -->
    <el-card class="log-card">
      <template #header>
        <div class="card-header">
          <span>配置变更日志</span>
          <el-button type="text" @click="showLogs = !showLogs">
            {{ showLogs ? '隐藏' : '显示' }}
          </el-button>
        </div>
      </template>
      
      <el-timeline v-if="showLogs">
        <el-timeline-item
          v-for="log in configLogs"
          :key="log.id"
          :timestamp="log.time"
          :type="log.action === 'UPDATE' ? 'warning' : 'success'"
        >
          <div>
            <strong>{{ log.admin }}</strong> 
            {{ log.action === 'UPDATE' ? '修改了' : '创建了' }} 
            <code>{{ log.config_key }}</code>
          </div>
          <div v-if="log.old_value" style="font-size: 12px; color: #999;">
            原值: {{ log.old_value }}
          </div>
          <div style="font-size: 12px; color: #666;">
            IP: {{ log.ip }} | {{ log.time }}
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

export default {
  name: 'SystemConfig',
  setup() {
    const activeConfigTab = ref('datasource')
    const saving = ref(false)
    const loading = ref(false)
    const showLogs = ref(true)
    
    // 表单引用
    const datasourceForm = ref(null)
    const cacheForm = ref(null)
    const logForm = ref(null)
    const systemForm = ref(null)
    
    // 配置数据
    const config = reactive({
      datasource: {
        api_url: '',
        db_host: '',
        db_port: 3306,
        db_name: '',
        db_user: '',
        db_password: '',
        spider_source: 'internal'
      },
      cache: {
        enabled: true,
        expire_time: 3600,
        capacity: 512,
        strategy: 'LRU'
      },
      log: {
        level: 'INFO',
        file_size: 100,
        keep_days: 30,
        output: ['console', 'file']
      },
      system: {
        timeout: 30,
        max_concurrent: 1000,
        max_file_size: 10,
        file_types: ['image', 'document'],
        session_timeout: 30,
        password_retry: 5
      }
    })
    
    // 配置变更日志
    const configLogs = ref([])
    
    // 获取配置
    const fetchConfig = async () => {
      loading.value = true
      try {
        const res = await request.get('/admin/system/config')
        if (res.data.success) {
          // 合并配置
          Object.assign(config.datasource, res.data.data.datasource || {})
          Object.assign(config.cache, res.data.data.cache || {})
          Object.assign(config.log, res.data.data.log || {})
          Object.assign(config.system, res.data.data.system || {})
          ElMessage.success('配置加载成功')
        }
      } catch (error) {
        ElMessage.error('获取配置失败')
      } finally {
        loading.value = false
      }
    }
    
    // 获取日志
    const fetchLogs = async () => {
      try {
        const res = await request.get('/admin/system/config/logs')
        if (res.data.success) {
          configLogs.value = res.data.data
        }
      } catch (error) {
        console.error('获取日志失败:', error)
      }
    }
    
    // 验证单个字段
    const validateField = async (type, key, value) => {
      try {
        const res = await request.post('/admin/system/config/validate', {
          type,
          key,
          value
        })
        return res.data
      } catch (error) {
        return { success: false, errors: ['验证服务出错'] }
      }
    }
    
    // 保存配置
    const handleSave = async () => {
      // 验证所有表单
      const forms = [datasourceForm, cacheForm, logForm, systemForm]
      for (const form of forms) {
        if (form.value) {
          try {
            await form.value.validate()
          } catch {
            ElMessage.warning('请检查表单填写是否正确')
            return
          }
        }
      }
      
      saving.value = true
      try {
        const res = await request.post('/admin/system/config', config)
        if (res.data.success) {
          ElMessage.success('配置保存成功')
          await fetchLogs()  // 刷新日志
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '保存失败')
      } finally {
        saving.value = false
      }
    }
    
    // 重置配置
    const handleReset = () => {
      ElMessageBox.confirm('确定要重置所有配置吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        fetchConfig()
        ElMessage.success('配置已重置')
      }).catch(() => {})
    }
    
    onMounted(() => {
      fetchConfig()
      fetchLogs()
    })
    
    return {
      activeConfigTab,
      config,
      saving,
      loading,
      showLogs,
      configLogs,
      datasourceForm,
      cacheForm,
      logForm,
      systemForm,
      handleSave,
      handleReset,
      fetchConfig
    }
  }
}
</script>

<style scoped>
.system-config {
  padding: 20px;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
}

.unit {
  margin-left: 10px;
  color: #999;
}

.log-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>