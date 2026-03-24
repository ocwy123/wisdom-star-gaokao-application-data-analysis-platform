<template>
  <div class="filter-panel">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>筛选条件</span>
          <el-button type="text" @click="handleReset">重置</el-button>
        </div>
      </template>
      
      <el-form :model="filterForm" label-width="100px">
        <el-form-item label="省份">
          <el-select v-model="filterForm.province" placeholder="全部" clearable>
            <el-option
              v-for="p in provinces"
              :key="p"
              :label="p"
              :value="p"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="学校类型">
          <el-select v-model="filterForm.schoolType" placeholder="全部" clearable>
            <el-option
              v-for="t in schoolTypes"
              :key="t"
              :label="t"
              :value="t"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="年份">
          <el-select v-model="filterForm.year" placeholder="全部" clearable>
            <el-option
              v-for="y in years"
              :key="y"
              :label="y"
              :value="y"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="分数范围">
          <el-slider
            v-model="filterForm.scoreRange"
            range
            :min="0"
            :max="750"
          />
        </el-form-item>
        
        <el-form-item label="985/211">
          <el-checkbox v-model="filterForm.is985">985院校</el-checkbox>
          <el-checkbox v-model="filterForm.is211">211院校</el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleFilter">应用筛选</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'FilterPanel',
  props: {
    provinces: {
      type: Array,
      default: () => []
    },
    schoolTypes: {
      type: Array,
      default: () => []
    },
    years: {
      type: Array,
      default: () => []
    }
  },
  emits: ['filter', 'reset'],
  data() {
    return {
      filterForm: {
        province: '',
        schoolType: '',
        year: '',
        scoreRange: [0, 750],
        is985: false,
        is211: false
      }
    }
  },
  methods: {
    handleFilter() {
      this.$emit('filter', this.filterForm)
    },
    handleReset() {
      this.filterForm = {
        province: '',
        schoolType: '',
        year: '',
        scoreRange: [0, 750],
        is985: false,
        is211: false
      }
      this.$emit('reset')
    }
  }
}
</script>