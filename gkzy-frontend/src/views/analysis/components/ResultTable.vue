<template>
  <div class="result-table">
    <el-table :data="results" border stripe v-loading="loading">
      <el-table-column prop="type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="getTypeTag(row.type)">
            {{ getTypeName(row.type) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="name" label="名称" min-width="200">
        <template #default="{ row }">
          <div class="result-name">
            <span>{{ row.name || row.school_name || row.major_name }}</span>
            <el-tag v-if="row.is_985" size="small" type="danger">985</el-tag>
            <el-tag v-if="row.is_211" size="small" type="warning">211</el-tag>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="province" label="省份" width="120" />
      <el-table-column prop="heat_score" label="热度" width="100" />
      <el-table-column prop="avg_salary" label="平均薪资" width="120">
        <template #default="{ row }">
          {{ row.avg_salary ? '¥' + row.avg_salary.toLocaleString() : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="min_score" label="最低分数" width="100" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResultTable',
  props: {
    results: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    total: {
      type: Number,
      default: 0
    },
    currentPage: {
      type: Number,
      default: 1
    },
    pageSize: {
      type: Number,
      default: 20
    }
  },
  emits: ['page-change', 'view-detail'],
  methods: {
    getTypeTag(type) {
      const map = {
        school: 'success',
        major: 'warning',
        employment: 'info',
        admission: 'primary',
        heat: 'danger'
      }
      return map[type] || 'info'
    },
    getTypeName(type) {
      const map = {
        school: '学校',
        major: '专业',
        employment: '就业',
        admission: '招生',
        heat: '热度'
      }
      return map[type] || type
    },
    handlePageChange(page) {
      this.$emit('page-change', page)
    },
    viewDetail(row) {
      this.$emit('view-detail', row)
    }
  }
}
</script>

<style scoped>
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.result-name {
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>