<template>
  <div class="multi-dimension-analysis">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>多维对比分析</h2>
      <div class="header-actions">
        <el-button type="primary" @click="addComparison">
          <el-icon><Plus /></el-icon> 新建对比
        </el-button>
        <el-button @click="saveComparison">
          <el-icon><Folder /></el-icon> 保存对比
        </el-button>
        <el-button @click="exportAnalysis">
          <el-icon><Download /></el-icon> 导出报告
        </el-button>
      </div>
    </div>

    <!-- 对比维度选择 - 隐藏单选圈，文字居中 -->
    <el-card class="dimension-card">
      <template #header>
        <div class="card-header">
          <span>选择对比维度（单选）</span>
          <el-button type="text" @click="resetDimensions">重置</el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6" v-for="dim in dimensionOptions" :key="dim.value">
          <div 
            class="dimension-item" 
            :class="{ active: selectedDimension === dim.value }"
            @click="selectedDimension = dim.value"
          >
            <el-icon :size="32"><component :is="dim.icon" /></el-icon>
            <span>{{ dim.label }}</span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 对比对象选择 -->
    <el-card class="compare-card" v-if="selectedDimension">
      <template #header>
        <div class="card-header">
          <span>选择对比对象 - {{ getDimensionLabel(selectedDimension) }}</span>
          <el-button type="text" @click="showComparePanel = !showComparePanel">
            {{ showComparePanel ? '收起' : '展开' }}
          </el-button>
        </div>
      </template>
      
      <el-collapse-transition>
        <div v-show="showComparePanel">
          <!-- 学校对比 -->
          <div v-if="selectedDimension === 'school'">
            <el-transfer
              v-model="selectedSchools"
              :data="schoolOptions"
              :titles="['可选学校', '已选学校']"
              filterable
              filter-placeholder="搜索学校"
            />
          </div>
          
          <!-- 专业对比 -->
          <div v-else-if="selectedDimension === 'major'">
            <el-transfer
              v-model="selectedMajors"
              :data="majorOptions"
              :titles="['可选专业', '已选专业']"
              filterable
              filter-placeholder="搜索专业"
            />
          </div>
          
          <!-- 省份对比 -->
          <div v-else-if="selectedDimension === 'province'">
            <el-transfer
              v-model="selectedProvinces"
              :data="provinceOptions"
              :titles="['可选省份', '已选省份']"
              filterable
              filter-placeholder="搜索省份"
            />
          </div>
          
          <!-- 热度分析 -->
          <div v-else-if="selectedDimension === 'heat'">
            <el-select v-model="selectedHeatType" placeholder="请选择热度类型" clearable>
              <el-option label="搜索热度" value="search" />
              <el-option label="收藏热度" value="favorite" />
              <el-option label="浏览热度" value="view" />
              <el-option label="综合热度" value="comprehensive" />
            </el-select>
          </div>
        </div>
      </el-collapse-transition>
    </el-card>

    <!-- 指标选择 - 添加更多指标 -->
    <el-card class="metric-card" v-if="selectedDimension">
      <template #header>
        <div class="card-header">
          <span>选择分析指标（可多选）</span>
          <el-checkbox v-model="selectAllMetrics" @change="toggleAllMetrics">
            全选
          </el-checkbox>
        </div>
      </template>
      
      <el-checkbox-group v-model="selectedMetrics">
        <el-row :gutter="20">
          <el-col :span="6" v-for="metric in commonMetrics" :key="metric.value">
            <el-checkbox :label="metric.value">
              {{ metric.label }}
            </el-checkbox>
          </el-col>
        </el-row>
      </el-checkbox-group>
    </el-card>

    <!-- 分析按钮 -->
    <div class="action-bar" v-if="selectedDimension">
      <el-button type="primary" size="large" @click="runAnalysis" :loading="analyzing">
        <el-icon><DataAnalysis /></el-icon> 开始分析
      </el-button>
    </div>

    <!-- 分析结果 -->
    <el-card class="result-card" v-if="analysisResult.length > 0">
      <template #header>
        <div class="card-header">
          <span>分析结果</span>
          <el-radio-group v-model="resultViewMode" size="small">
            <el-radio-button label="table">表格</el-radio-button>
            <el-radio-button label="chart">图表</el-radio-button>
            <el-radio-button label="radar">雷达图</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
        <!-- 表格视图 - 显示所有选中的指标 -->
        <div v-if="resultViewMode === 'table'">
          <el-table 
            :data="analysisResult" 
            border 
            stripe 
            style="width: 100%"
            :header-cell-style="{ background: '#f5f7fa', color: '#333', fontWeight: 'bold' }"
            align="left"
            header-align="left"
          >
            <!-- 对比项列 -->
            <el-table-column 
              prop="dimension_value" 
              label="对比项" 
              fixed 
              width="150"
            />
    <el-table-column
      v-for="metric in selectedMetrics"
      :key="metric"
      :label="getMetricLabel(metric)"
      :width="150"
    >
      <template #default="{ row }">
        {{ formatMetricValue(row.data[metric], metric) }}
      </template>
    </el-table-column>
  </el-table>
</div>
      <!-- 图表视图 -->
      <div v-else-if="resultViewMode === 'chart'" class="chart-container">
        <div ref="compareChart" style="width: 100%; height: 400px;"></div>
      </div>
      
      <!-- 雷达图视图 -->
      <div v-else-if="resultViewMode === 'radar'" class="chart-container">
        <div ref="radarChart" style="width: 100%; height: 400px;"></div>
      </div>
    </el-card>

    <!-- 保存对比对话框 -->
    <el-dialog v-model="saveDialogVisible" title="保存对比分析" width="400px">
      <el-form :model="saveForm">
        <el-form-item label="对比名称">
          <el-input v-model="saveForm.name" placeholder="请输入对比名称" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="saveForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doSaveComparison">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Folder, Download, DataAnalysis } from '@element-plus/icons-vue'
import request from '@/utils/request'
import * as echarts from 'echarts'

export default {
  name: 'MultiDimensionAnalysis',
  components: {
    Plus, Folder, Download, DataAnalysis
  },
  setup() {
    // 维度选项（单选）
    const selectedDimension = ref('')
    const dimensionOptions = [
      { value: 'school', label: '学校对比', icon: 'School' },
      { value: 'major', label: '专业对比', icon: 'Reading' },
      { value: 'province', label: '地域对比', icon: 'Location' },
      { value: 'heat', label: '热度分析', icon: 'Fire' }
    ]
    
    // 通用指标选项（所有维度都可用）
    const commonMetrics = [
      { value: 'avg_score', label: '平均分' },
      { value: 'min_score', label: '最低分' },
      { value: 'max_score', label: '最高分' },
      { value: 'admission_count', label: '录取人数' },
      { value: 'avg_salary', label: '平均薪资' },
      { value: 'heat_score', label: '综合热度' },
      { value: 'search_count', label: '搜索量' },
      { value: 'favorite_count', label: '收藏量' },
      { value: 'view_count', label: '浏览量' },
      { value: 'school_count', label: '学校数量' },
      { value: 'city_count', label: '城市数量' },
      { value: '985_count', label: '985院校数' },
      { value: '211_count', label: '211院校数' },
      { value: 'double_first_count', label: '双一流院校数' },
      { value: 'phd_count', label: '博士点数量' },
      { value: 'master_count', label: '硕士点数量' }
    ]
    
    // 状态
    const selectedMetrics = ref(['avg_score', 'heat_score', 'admission_rate', 'avg_salary'])
    const selectAllMetrics = ref(false)
    const showComparePanel = ref(true)
    const analyzing = ref(false)
    const analysisResult = ref([])
    const resultViewMode = ref('table')
    
    // 对比对象
    const selectedSchools = ref([])
    const selectedMajors = ref([])
    const selectedProvinces = ref([])
    const selectedYears = ref([2020, 2024])
    const selectedScoreSegment = ref('')
    const selectedHeatType = ref('comprehensive')
    
    // 选项数据
    const schoolOptions = ref([])
    const majorOptions = ref([])
    const provinceOptions = ref([])
    
    // 图表引用
    const compareChart = ref(null)
    const radarChart = ref(null)
    
    // 保存对话框
    const saveDialogVisible = ref(false)
    const saveForm = reactive({
      name: '',
      description: ''
    })
    
    const yearMarks = {
      2018: '2018',
      2019: '2019',
      2020: '2020',
      2021: '2021',
      2022: '2022',
      2023: '2023',
      2024: '2024'
    }
    
    // 获取维度标签
    const getDimensionLabel = (value) => {
      const dim = dimensionOptions.find(d => d.value === value)
      return dim ? dim.label : value
    }
    
    // 获取选项数据
    const fetchOptions = async () => {
      try {
        const res = await request.get('/analysis/filters')
        console.log('筛选选项返回:', res.data)
        if (res.data.success) {
          // 学校选项
          schoolOptions.value = res.data.data.schools?.map(s => ({
            key: s.id,
            label: s.name
          })) || []
          
          // 专业选项
          majorOptions.value = res.data.data.majors?.map(m => ({
            key: m.id,
            label: m.name
          })) || []
          
          // 省份选项
          provinceOptions.value = res.data.data.provinces?.map(p => ({
            key: p,
            label: p
          })) || []
          
          console.log('学校选项:', schoolOptions.value)
        }
      } catch (error) {
        console.error('获取选项失败:', error)
      }
    }
    
    // 重置维度
    const resetDimensions = () => {
      selectedDimension.value = ''
      selectedSchools.value = []
      selectedMajors.value = []
      selectedProvinces.value = []
      selectedYears.value = [2020, 2024]
      selectedScoreSegment.value = ''
      selectedHeatType.value = 'comprehensive'
      selectedMetrics.value = ['avg_score', 'heat_score', 'admission_rate', 'avg_salary']
    }
    
    // 全选指标
    const toggleAllMetrics = (val) => {
      if (val) {
        selectedMetrics.value = commonMetrics.map(m => m.value)
      } else {
        selectedMetrics.value = []
      }
    }
    
    // 监听选中指标变化
    watch(selectedMetrics, (val) => {
      selectAllMetrics.value = val.length === commonMetrics.length
    })
    
    // 监听视图模式变化
    watch(resultViewMode, (newMode) => {
      if (analysisResult.value.length > 0) {
        nextTick(() => {
          if (newMode === 'chart') {
            initCompareChart()
          } else if (newMode === 'radar') {
            initRadarChart()
          }
        })
      }
    })
    
    // 获取指标标签
    const getMetricLabel = (value) => {
      const metric = commonMetrics.find(m => m.value === value)
      return metric ? metric.label : value
    }
    
    // 格式化指标值
    const formatMetricValue = (value, metric) => {
      if (value === undefined || value === null) return '-'
      
      if (metric.includes('score') || metric.includes('salary')) {
        return Number(value).toLocaleString()
      }
      if (metric.includes('rate')) {
        return (Number(value) * 100).toFixed(2) + '%'
      }
      if (metric.includes('count')) {
        return Number(value).toLocaleString()
      }
      if (metric.includes('growth')) {
        return Number(value).toFixed(2) + '%'
      }
      if (metric.includes('quality')) {
        return Number(value).toFixed(2)
      }
      return value
    }
    
    // 初始化对比图表
    const initCompareChart = () => {
      if (!compareChart.value || analysisResult.value.length === 0) return
      
      // 销毁旧图表
      if (compareChart.value.chart) {
        compareChart.value.chart.dispose()
      }
      
      const chart = echarts.init(compareChart.value)
      compareChart.value.chart = chart
      
      const dimensions = analysisResult.value.map(item => item.dimension_value)
      const series = selectedMetrics.value.map(metric => ({
        name: getMetricLabel(metric),
        type: 'bar',
        data: analysisResult.value.map(item => item.data[metric] || 0)
      }))
      
      chart.setOption({
        title: {
          text: '多维对比分析',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        legend: {
          data: series.map(s => s.name),
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dimensions,
          axisLabel: { rotate: 30 }
        },
        yAxis: {
          type: 'value',
          name: '数值'
        },
        series: series
      })
      
      // 窗口大小变化时自适应
      window.addEventListener('resize', () => {
        chart.resize()
      })
    }
    
    // 初始化雷达图
    const initRadarChart = () => {
      if (!radarChart.value || analysisResult.value.length === 0) return
      
      // 销毁旧图表
      if (radarChart.value.chart) {
        radarChart.value.chart.dispose()
      }
      
      const chart = echarts.init(radarChart.value)
      radarChart.value.chart = chart
      
      // 计算每个指标的最大值
      const maxValues = {}
      selectedMetrics.value.forEach(metric => {
        maxValues[metric] = Math.max(
          ...analysisResult.value.map(item => item.data[metric] || 0)
        ) * 1.2 || 100
      })
      
      const indicators = selectedMetrics.value.map(metric => ({
        name: getMetricLabel(metric),
        max: maxValues[metric]
      }))
      
      const seriesData = analysisResult.value.map(item => ({
        value: selectedMetrics.value.map(metric => item.data[metric] || 0),
        name: item.dimension_value,
        areaStyle: { color: 'rgba(64,158,255,0.2)' }
      }))
      
      chart.setOption({
        title: {
          text: '雷达对比分析',
          left: 'center'
        },
        tooltip: {},
        legend: {
          data: analysisResult.value.map(item => item.dimension_value),
          orient: 'vertical',
          left: 'left',
          top: 'center'
        },
        radar: {
          indicator: indicators,
          center: ['50%', '50%'],
          radius: '65%',
          shape: 'circle',
          name: { textStyle: { color: '#666' } }
        },
        series: [{
          type: 'radar',
          data: seriesData,
          lineStyle: { width: 2 },
          areaStyle: { opacity: 0.2 }
        }]
      })
      
      window.addEventListener('resize', () => {
        chart.resize()
      })
    }
    
    // 运行分析
    const runAnalysis = async () => {
      // 验证是否选择了对比对象
      if (selectedDimension.value === 'school' && selectedSchools.value.length === 0) {
        ElMessage.warning('请至少选择一个学校')
        return
      }
      if (selectedDimension.value === 'major' && selectedMajors.value.length === 0) {
        ElMessage.warning('请至少选择一个专业')
        return
      }
      if (selectedDimension.value === 'province' && selectedProvinces.value.length === 0) {
        ElMessage.warning('请至少选择一个省份')
        return
      }
      analyzing.value = true
      try {
        // 构建请求参数
        const params = {
          dimension: selectedDimension.value,
          metrics: selectedMetrics.value,
          filters: {},
          time_range: selectedYears.value
        }
        
        // 根据维度添加对应的筛选条件
        if (selectedDimension.value === 'school') {
          params.filters.school_ids = selectedSchools.value
        } else if (selectedDimension.value === 'major') {
          params.filters.major_ids = selectedMajors.value
        } else if (selectedDimension.value === 'province') {
          params.filters.provinces = selectedProvinces.value
        } else if (selectedDimension.value === 'score') {
          params.filters.score_segment = selectedScoreSegment.value
        } else if (selectedDimension.value === 'heat') {
          params.filters.heat_type = selectedHeatType.value
        }
        
        const res = await request.post('/analysis/compare', params)
        
        if (res.data.success) {
          analysisResult.value = res.data.data.data || []
          
          // 根据当前视图模式渲染不同的图表
          nextTick(() => {
            if (resultViewMode.value === 'chart') {
              initCompareChart()
            } else if (resultViewMode.value === 'radar') {
              initRadarChart()
            }
          })
          
          ElMessage.success('分析完成')
        }
      } catch (error) {
        ElMessage.error('分析失败')
      } finally {
        analyzing.value = false
      }
    }
    
    // 添加对比
    const addComparison = () => {
      resetDimensions()
      ElMessage.success('已重置，可以开始新的对比')
    }
    
    // 保存对比
    const saveComparison = () => {
      if (analysisResult.value.length === 0) {
        ElMessage.warning('请先运行分析')
        return
      }
      saveDialogVisible.value = true
    }
    
    // 执行保存
    const doSaveComparison = () => {
      if (!saveForm.name) {
        ElMessage.warning('请输入对比名称')
        return
      }
      
      // 保存到 localStorage
      const savedComparisons = JSON.parse(localStorage.getItem('savedComparisons') || '[]')
      savedComparisons.push({
        id: Date.now(),
        name: saveForm.name,
        description: saveForm.description,
        dimension: selectedDimension.value,
        metrics: selectedMetrics.value,
        result: analysisResult.value,
        createTime: new Date().toLocaleString()
      })
      localStorage.setItem('savedComparisons', JSON.stringify(savedComparisons))
      
      saveDialogVisible.value = false
      saveForm.name = ''
      saveForm.description = ''
      ElMessage.success('保存成功')
    }
    
    // 导出分析
    const exportAnalysis = async () => {
      if (analysisResult.value.length === 0) {
        ElMessage.warning('请先运行分析')
        return
      }
      
      try {
        const res = await request.post('/analysis/export', {
          type: 'excel',
          data: analysisResult.value,
          dimension: selectedDimension.value,
          metrics: selectedMetrics.value
        })
        
        if (res.data.success) {
          // 解码 base64 并下载 Excel 文件
          const excelData = res.data.data
          const blob = base64ToBlob(excelData, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
          const link = document.createElement('a')
          link.href = URL.createObjectURL(blob)
          link.download = res.data.filename || `analysis_${new Date().getTime()}.xlsx`
          link.click()
          URL.revokeObjectURL(link.href)
          ElMessage.success('导出成功')
        }
      } catch (error) {
        console.error('导出失败:', error)
        ElMessage.error('导出失败：' + (error.response?.data?.message || '未知错误'))
      }
    }
    
    // base64 转 Blob 工具函数
    const base64ToBlob = (base64Data, contentType) => {
      const byteCharacters = atob(base64Data)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      return new Blob([byteArray], { type: contentType })
    }
    
    onMounted(() => {
      fetchOptions()
    })
    
    return {
      selectedDimension,
      dimensionOptions,
      commonMetrics,
      selectedMetrics,
      selectAllMetrics,
      showComparePanel,
      analyzing,
      analysisResult,
      resultViewMode,
      selectedSchools,
      selectedMajors,
      selectedProvinces,
      selectedYears,
      selectedScoreSegment,
      selectedHeatType,
      schoolOptions,
      majorOptions,
      provinceOptions,
      yearMarks,
      saveDialogVisible,
      saveForm,
      compareChart,
      radarChart,
      getDimensionLabel,
      getMetricLabel,
      formatMetricValue,
      toggleAllMetrics,
      resetDimensions,
      runAnalysis,
      addComparison,
      saveComparison,
      doSaveComparison,
      exportAnalysis
    }
  }
}
</script>

<style scoped>
.multi-dimension-analysis {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.dimension-card,
.compare-card,
.metric-card,
.result-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dimension-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 120px;  /* 固定高度 */
  box-sizing: border-box;
}

.dimension-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64,158,255,0.2);
}

.dimension-item.active {
  border-color: #409eff;
  background-color: #ecf5ff;
  color: #409eff;
}

.dimension-item .el-icon {
  font-size: 32px;
  margin: 0;
  padding: 0;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;  /* 固定图标区域高度 */
}

.dimension-item span {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.2;
  margin: 5px 0 0 0;
  padding: 0;
  display: block;
}
.action-bar {
  text-align: center;
  margin: 30px 0;
}

.action-bar .el-button {
  min-width: 200px;
}

.chart-container {
  padding: 20px;
}

:deep(.el-transfer) {
  display: flex;
  justify-content: center;
  gap: 40px;
}

:deep(.el-transfer-panel) {
  width: 300px;
}

:deep(.el-slider) {
  padding: 0 20px;
}
</style>