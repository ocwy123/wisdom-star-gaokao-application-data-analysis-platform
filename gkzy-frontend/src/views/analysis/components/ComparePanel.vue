<template>
  <div class="compare-panel">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>对比分析</span>
        </div>
      </template>
      
      <el-form :model="compareForm" label-width="120px">
        <el-form-item label="对比维度">
          <el-checkbox-group v-model="compareForm.dimensions">
            <el-checkbox label="school">学校</el-checkbox>
            <el-checkbox label="major">专业</el-checkbox>
            <el-checkbox label="province">省份</el-checkbox>
            <el-checkbox label="year">年份</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="分析指标">
          <el-checkbox-group v-model="compareForm.metrics">
            <el-checkbox label="avg_score">平均分</el-checkbox>
            <el-checkbox label="min_score">最低分</el-checkbox>
            <el-checkbox label="avg_salary">平均薪资</el-checkbox>
            <el-checkbox label="heat_score">热度</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="对比对象">
          <el-select
            v-model="compareForm.targets"
            multiple
            filterable
            placeholder="请选择对比对象"
          >
            <el-option
              v-for="item in targetOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleCompare">开始对比</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'ComparePanel',
  props: {
    targetOptions: {
      type: Array,
      default: () => []
    }
  },
  emits: ['compare', 'reset'],
  data() {
    return {
      compareForm: {
        dimensions: ['school', 'major'],
        metrics: ['avg_score', 'heat_score'],
        targets: []
      }
    }
  },
  methods: {
    handleCompare() {
      this.$emit('compare', this.compareForm)
    },
    handleReset() {
      this.compareForm = {
        dimensions: ['school', 'major'],
        metrics: ['avg_score', 'heat_score'],
        targets: []
      }
      this.$emit('reset')
    }
  }
}
</script>