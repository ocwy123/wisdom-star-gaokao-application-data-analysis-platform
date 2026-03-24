<template>
  <div class="search-panel">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>搜索面板</span>
        </div>
      </template>
      
      <el-form :model="searchForm" label-width="100px">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="输入搜索关键词" />
        </el-form-item>
        
        <el-form-item label="搜索类型">
          <el-checkbox-group v-model="searchForm.types">
            <el-checkbox label="school">学校</el-checkbox>
            <el-checkbox label="major">专业</el-checkbox>
            <el-checkbox label="employment">就业</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="省份">
          <el-select v-model="searchForm.province" placeholder="全部" clearable>
            <el-option
              v-for="p in provinces"
              :key="p"
              :label="p"
              :value="p"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'SearchPanel',
  props: {
    provinces: {
      type: Array,
      default: () => []
    }
  },
  emits: ['search', 'reset'],
  data() {
    return {
      searchForm: {
        keyword: '',
        types: ['school', 'major', 'employment'],
        province: ''
      }
    }
  },
  methods: {
    handleSearch() {
      this.$emit('search', this.searchForm)
    },
    handleReset() {
      this.searchForm = {
        keyword: '',
        types: ['school', 'major', 'employment'],
        province: ''
      }
      this.$emit('reset')
    }
  }
}
</script>