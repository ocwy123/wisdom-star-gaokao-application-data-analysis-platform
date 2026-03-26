<template>
  <div class="data-import">
    <!-- 导入按钮 -->
    <el-button type="primary" @click="showImportDialog = true">
      <el-icon><Upload /></el-icon>
      数据导入
    </el-button>

    <!-- 导入对话框 -->
    <el-dialog 
      v-model="showImportDialog" 
      title="数据导入" 
      width="80%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="!importing"
    >
      <div class="import-container">
        <!-- 左侧配置区域 -->
        <div class="config-panel">
          <el-form :model="importForm" label-width="100px">
            <el-form-item label="文件类型">
              <el-radio-group v-model="importForm.fileType">
                <el-radio label="csv">CSV</el-radio>
                <el-radio label="excel">Excel</el-radio>
                <el-radio label="jl">JL</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="目标数据表">
              <el-select v-model="importForm.targetTable" placeholder="请选择数据表">
                <el-option label="高校信息表 (edu_school)" value="edu_school" />
                <el-option label="专业信息表 (edu_major)" value="edu_major" />
                <el-option label="高校专业关系表 (edu_school_major)" value="edu_school_major" />
                <el-option label="招生录取数据表 (edu_adm_record)" value="edu_adm_record" />
                <el-option label="高校热度统计表 (ana_school_heat)" value="ana_school_heat" />
                <el-option label="专业就业数据表 (ana_major_employment)" value="ana_major_employment" />
                <el-option label="一分一段表 (ana_score_segment)" value="ana_score_segment" />
              </el-select>
            </el-form-item>

            <el-form-item label="选择文件">
              <el-upload
                class="upload-demo"
                :action="uploadUrl"
                :before-upload="beforeUpload"
                :on-success="handleUploadSuccess"
                :on-error="handleUploadError"
                :show-file-list="false"
                :disabled="importing"
              >
                <el-button :disabled="importing">
                  <el-icon><Upload /></el-icon>
                  选择文件
                </el-button>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 {{ getFileExtensions() }} 格式文件
                  </div>
                </template>
              </el-upload>
              
              <div v-if="importForm.fileName" class="file-info">
                <el-icon><Document /></el-icon>
                {{ importForm.fileName }}
              </div>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="startImport" 
                :loading="importing"
                :disabled="!importForm.fileName || !importForm.targetTable"
              >
                {{ importing ? '导入中...' : '开始导入' }}
              </el-button>
              <el-button @click="cancelImport" :disabled="importing">取消</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 右侧控制台区域 -->
        <div class="console-panel">
          <div class="console-header">
            <span>控制台输出</span>
            <el-button size="small" @click="clearLogs" :disabled="importing">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
          </div>
          <div class="console-content" ref="consoleRef">
            <div 
              v-for="(log, index) in logs" 
              :key="index" 
              class="log-item"
              :class="getLogClass(log.type)"
            >
              <span class="log-time">{{ log.time }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
            <div v-if="logs.length === 0" class="empty-log">
              暂无内容
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Document, Delete } from '@element-plus/icons-vue'
import request from '../../../utils/request'

const showImportDialog = ref(false)
const importing = ref(false)
const consoleRef = ref(null)

const importForm = reactive({
  fileType: 'csv',
  targetTable: '',
  fileName: '',
  filePath: ''
})

const logs = ref([])

const uploadUrl = computed(() => {
  return '/api/admin/upload'
})

const getFileExtensions = () => {
  const extensions = {
    csv: '.csv',
    excel: '.xlsx, .xls',
    jl: '.jl'
  }
  return extensions[importForm.fileType] || '.csv'
}

const beforeUpload = (file) => {
  const allowedTypes = {
    csv: ['text/csv', 'application/vnd.ms-excel'],
    excel: ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'],
    jl: ['application/json', 'text/plain']
  }

  const currentTypes = allowedTypes[importForm.fileType]
  if (!currentTypes.includes(file.type) && file.type !== '') {
    ElMessage.error(`请选择${getFileExtensions()}格式的文件`)
    return false
  }

  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }

  return true
}

const handleUploadSuccess = (response) => {
  if (response.success) {
    importForm.fileName = response.data.fileName
    importForm.filePath = response.data.filePath
    addLog('success', `文件上传成功: ${importForm.fileName}`)
  } else {
    ElMessage.error(response.message || '文件上传失败')
  }
}

const handleUploadError = (error) => {
  ElMessage.error('文件上传失败')
  console.error('Upload error:', error)
}

const addLog = (type, message) => {
  const time = new Date().toLocaleTimeString()
  logs.value.push({
    type,
    time,
    message
  })
  
  // 自动滚动到底部
  nextTick(() => {
    if (consoleRef.value) {
      consoleRef.value.scrollTop = consoleRef.value.scrollHeight
    }
  })
}

const getLogClass = (type) => {
  return {
    'log-info': type === 'info',
    'log-success': type === 'success',
    'log-warning': type === 'warning',
    'log-error': type === 'error'
  }
}

const startImport = async () => {
  if (!importForm.fileName || !importForm.targetTable) {
    ElMessage.warning('请选择文件和目标数据表')
    return
  }

  importing.value = true
  addLog('info', '开始数据导入...')

  try {
    const response = await request.post('/api/admin/data-import', {
      fileType: importForm.fileType,
      targetTable: importForm.targetTable,
      filePath: importForm.filePath
    })

    if (response.data.success) {
      // 显示后端返回的详细日志
      if (response.data.logs && response.data.logs.length > 0) {
        response.data.logs.forEach(log => {
          addLog(log.type, log.message)
        })
      }
      
      addLog('success', '数据导入完成')
      ElMessage.success('数据导入完成')
    } else {
      addLog('error', `导入失败: ${response.data.message}`)
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    addLog('error', `导入错误: ${error.message}`)
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

const cancelImport = () => {
  if (importing.value) {
    ElMessage.warning('导入正在进行中，无法取消')
    return
  }
  resetForm()
  showImportDialog.value = false
}

const clearLogs = () => {
  logs.value = []
}

const resetForm = () => {
  importForm.fileName = ''
  importForm.filePath = ''
  importForm.targetTable = ''
  logs.value = []
  importing.value = false
}

// 监听对话框关闭
const handleDialogClose = () => {
  if (!importing.value) {
    resetForm()
  }
}
</script>

<style scoped>
.import-container {
  display: flex;
  height: 500px;
  gap: 20px;
}

.config-panel {
  flex: 1;
  padding: 20px;
  border-right: 1px solid #e4e7ed;
}

.console-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #1e1e1e;
  border-radius: 4px;
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: #2d2d30;
  color: #cccccc;
  border-bottom: 1px solid #3e3e42;
}

.console-content {
  flex: 1;
  padding: 15px;
  color: #d4d4d4;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  overflow-y: auto;
  white-space: pre-wrap;
}

.log-item {
  margin-bottom: 5px;
  padding: 2px 0;
}

.log-time {
  color: #6a9955;
  margin-right: 10px;
}

.log-info .log-message {
  color: #569cd6;
}

.log-success .log-message {
  color: #4ec9b0;
}

.log-warning .log-message {
  color: #ce9178;
}

.log-error .log-message {
  color: #f44747;
}

.empty-log {
  color: #6a9955;
  text-align: center;
  padding: 20px;
}

.file-info {
  margin-top: 10px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-demo {
  width: 100%;
}

.el-form-item {
  margin-bottom: 20px;
}
</style>