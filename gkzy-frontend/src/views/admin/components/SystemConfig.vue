<template>
  <div class="system-config">
    <el-tabs v-model="activeConfigTab" type="border-card">
      <!-- 数据源配置 -->
      <el-tab-pane label="数据源配置" name="datasource">
        <el-form :model="config.datasource" label-width="150px">
          <el-form-item label="API地址">
            <el-input v-model="config.datasource.api_url" placeholder="http://api.example.com" />
          </el-form-item>
          
          <el-form-item label="数据库主机">
            <el-input v-model="config.datasource.db_host" placeholder="localhost" />
          </el-form-item>
          
          <el-form-item label="数据库端口">
            <el-input-number v-model="config.datasource.db_port" :min="1" :max="65535" />
          </el-form-item>
          
          <el-form-item label="数据库名称">
            <el-input v-model="config.datasource.db_name" placeholder="gkzy" />
          </el-form-item>
          
          <el-form-item label="数据库用户名">
            <el-input v-model="config.datasource.db_user" placeholder="root" />
          </el-form-item>
          
          <el-form-item label="数据库密码">
            <el-input v-model="config.datasource.db_password" type="password" show-password />
          </el-form-item>
          
          <el-form-item label="爬虫数据源">
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
        <el-form :model="config.cache" label-width="150px">
          <el-form-item label="缓存开关">
            <el-switch v-model="config.cache.enabled" active-text="开启" inactive-text="关闭" />
          </el-form-item>
          
          <el-form-item label="缓存过期时间">
            <el-input-number v-model="config.cache.expire_time" :min="1" :max="86400" />
            <span class="unit">秒</span>
          </el-form-item>
          
          <el-form-item label="缓存容量">
            <el-input-number v-model="config.cache.capacity" :min="1" :max="10000" />
            <span class="unit">MB</span>
          </el-form-item>
          
          <el-form-item label="缓存策略">
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
        <el-form :model="config.log" label-width="150px">
          <el-form-item label="日志级别">
            <el-select v-model="config.log.level" placeholder="请选择日志级别">
              <el-option label="DEBUG" value="DEBUG" />
              <el-option label="INFO" value="INFO" />
              <el-option label="WARNING" value="WARNING" />
              <el-option label="ERROR" value="ERROR" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="日志文件大小">
            <el-input-number v-model="config.log.file_size" :min="1" :max="1024" />
            <span class="unit">MB</span>
          </el-form-item>
          
          <el-form-item label="日志保留天数">
            <el-input-number v-model="config.log.keep_days" :min="1" :max="365" />
            <span class="unit">天</span>
          </el-form-item>
          
          <el-form-item label="日志输出">
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
        <el-form :model="config.system" label-width="150px">
          <el-form-item label="超时时间">
            <el-input-number v-model="config.system.timeout" :min="1" :max="300" />
            <span class="unit">秒</span>
          </el-form-item>
          
          <el-form-item label="最大并发用户数">
            <el-input-number v-model="config.system.max_concurrent" :min="1" :max="10000" />
            <span class="unit">人</span>
          </el-form-item>
          
          <el-form-item label="文件上传大小限制">
            <el-input-number v-model="config.system.max_file_size" :min="1" :max="1024" />
            <span class="unit">MB</span>
          </el-form-item>
          
          <el-form-item label="允许文件类型">
            <el-select v-model="config.system.file_types" multiple placeholder="请选择">
              <el-option label="图片" value="image" />
              <el-option label="文档" value="document" />
              <el-option label="视频" value="video" />
              <el-option label="压缩包" value="archive" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="会话超时时间">
            <el-input-number v-model="config.system.session_timeout" :min="5" :max="1440" />
            <span class="unit">分钟</span>
          </el-form-item>
          
          <el-form-item label="密码重试次数">
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
      <el-button @click="handleRefresh">刷新</el-button>
    </div>
    
    <!-- 变更日志 -->
    <el-card class="log-card" v-if="showLogs">
      <template #header>
        <div class="card-header">
          <span>配置变更日志</span>
          <el-button type="text" @click="showLogs = !showLogs">隐藏</el-button>
        </div>
      </template>
      
      <el-timeline>
        <el-timeline-item
          v-for="(log, index) in configLogs"
          :key="index"
          :timestamp="log.time"
          :type="log.type"
        >
          {{ log.content }}
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
    const showLogs = ref(true)
    
    // 配置数据
    const config = reactive({
      datasource: {
        api_url: 'http://192.168.54.29:5000/api',
        db_host: '192.168.54.241',
        db_port: 3306,
        db_name: 'gkzy_mysql',
        db_user: 'root',
        db_password: 'root',
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
    const configLogs = ref([
      {
        time: '2026-03-19 10:23:45',
        content: '管理员 admin 修改了数据源配置',
        type: 'primary'
      },
      {
        time: '2026-03-18 15:12:30',
        content: '管理员 admin 修改了缓存策略',
        type: 'success'
      },
      {
        time: '2026-03-17 09:45:12',
        content: '管理员 admin 修改了日志级别为 INFO',
        type: 'info'
      }
    ])
    
    // 获取配置
    const fetchConfig = async () => {
      try {
        // 实际项目中从后端获取
        // const res = await request.get('/admin/system/config')
        // if (res.data.success) {
        //   Object.assign(config, res.data.data)
        // }
        ElMessage.success('配置已加载')
      } catch (error) {
        ElMessage.error('获取配置失败')
      }
    }
    
    // 验证配置
    const validateConfig = () => {
      // 验证API地址格式
      const urlPattern = /^https?:\/\/.+\..+/
      if (!urlPattern.test(config.datasource.api_url)) {
        ElMessage.warning('API地址格式不正确')
        return false
      }
      
      // 验证端口范围
      if (config.datasource.db_port < 1 || config.datasource.db_port > 65535) {
        ElMessage.warning('数据库端口必须在1-65535之间')
        return false
      }
      
      // 验证数字范围
      if (config.cache.expire_time < 1 || config.cache.expire_time > 86400) {
        ElMessage.warning('缓存过期时间必须在1-86400秒之间')
        return false
      }
      
      if (config.system.timeout < 1 || config.system.timeout > 300) {
        ElMessage.warning('超时时间必须在1-300秒之间')
        return false
      }
      
      return true
    }
    
    // 保存配置
    const handleSave = async () => {
      if (!validateConfig()) return
      
      saving.value = true
      try {
        // 实际项目中发送到后端
        // const res = await request.post('/admin/system/config', config)
        // if (res.data.success) {
        //   ElMessage.success('配置保存成功')
        //   // 添加日志
        //   configLogs.value.unshift({
        //     time: new Date().toLocaleString(),
        //     content: '管理员修改了系统配置',
        //     type: 'success'
        //   })
        // }
        
        // 模拟保存成功
        await new Promise(resolve => setTimeout(resolve, 1000))
        ElMessage.success('配置保存成功')
        
        // 添加日志
        configLogs.value.unshift({
          time: new Date().toLocaleString(),
          content: '管理员修改了系统配置',
          type: 'success'
        })
      } catch (error) {
        ElMessage.error('保存失败')
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
    
    // 刷新配置
    const handleRefresh = () => {
      fetchConfig()
    }
    
    onMounted(() => {
      fetchConfig()
    })
    
    return {
      activeConfigTab,
      config,
      saving,
      showLogs,
      configLogs,
      handleSave,
      handleReset,
      handleRefresh
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