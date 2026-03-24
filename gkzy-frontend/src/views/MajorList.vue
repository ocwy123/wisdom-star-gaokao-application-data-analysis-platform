<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElLoading } from 'element-plus'
import { getMajorList } from '../api/major'

const router = useRouter()
const majorList = ref([])
const total = ref(0)
const loading = ref(false)
const searchKeyword = ref('')
const pagination = ref({
  page: 1,
  size: 20
})

const loadMajors = async () => {
  const loadingInstance = ElLoading.service({ fullscreen: true, text: '加载中...' })
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      size: pagination.value.size
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    const res = await getMajorList(params)
    majorList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error('加载专业列表失败', error)
  } finally {
    loading.value = false
    loadingInstance.close()
  }
}

const viewDetail = (id) => {
  router.push(`/major/${id}`)
}

const handleSearch = () => {
  pagination.value.page = 1
  loadMajors()
}

const handlePageChange = (page) => {
  pagination.value.page = page
  loadMajors()
}

onMounted(() => {
  loadMajors()
})

watch(() => pagination.value.page, loadMajors)
</script>

<template>
  <div class="major-list-container">
    <!-- Hero 区域 -->
    <el-affix :offset="0">
      <div class="hero-section">
        <div class="hero-content">
          <h1>
            专业库
            <el-tag size="large" effect="dark" round>{{ total }}+ 个专业</el-tag>
          </h1>
          <p class="subtitle">全国高校专业信息查询与深度分析，助你科学选择未来方向</p>
        </div>
      </div>
    </el-affix>

    <!-- 搜索栏 -->
    <div class="search-wrapper">
      <el-input
        v-model="searchKeyword"
        placeholder="输入专业名称或代码"
        clearable
        @keyup.enter="handleSearch"
        class="search-input"
      >
        <template #prepend>
          <i class="fas fa-search"></i>
        </template>
        <template #append>
          <el-button :loading="loading" @click="handleSearch" type="primary">
            <i class="fas fa-search"></i> 搜索
          </el-button>
        </template>
      </el-input>
    </div>

    <!-- 列表区域 -->
    <div class="list-section">
      <!-- 空状态 -->
      <el-empty v-if="!loading && majorList.length === 0" description="暂无专业数据" />

      <!-- 专业卡片网格 -->
      <el-row v-else :gutter="20" class="major-grid">
        <el-col
          v-for="major in majorList"
          :key="major.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card
            class="major-card"
            :body-style="{ padding: '0px' }"
            shadow="hover"
            @click="viewDetail(major.id)"
          >
            <div class="card-header">
              <div class="title-wrapper">
                <h3>{{ major.name }}</h3>
                <el-tag size="small" type="info" effect="plain">{{ major.code }}</el-tag>
              </div>
              <i class="fas fa-chevron-right arrow"></i>
            </div>
            <div class="card-body">
              <p class="major-desc">{{ major.description?.substring(0, 80) }}...</p>
              <div class="major-meta">
                <span><i class="far fa-clock"></i> {{ major.duration }}年制</span>
                <span v-if="major.degree"><i class="fas fa-graduation-cap"></i> {{ major.degree }}</span>
              </div>
            </div>
            <div class="card-footer" v-if="major.subjects">
              <el-tag size="small" type="success" effect="light">
                <i class="fas fa-flask"></i> {{ major.subjects }}
              </el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 分页 -->
      <div v-if="total > pagination.size" class="pagination-wrapper">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pagination.size"
          :current-page="pagination.page"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 样式保持不变 */
.major-list-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 30px 40px;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0 0 50px 50px;
  margin: 0 30px 50px;
  padding: 30px;
  color: white;
  text-align: center;
}

.hero-content h1 {
  font-size: 3rem;
  margin: 0 0 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
  color: #ffffff;
}

.hero-content h1 .el-tag {
  font-size: 1.2rem;
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
}

.hero-content .subtitle {
  font-size: 1.3rem;
  opacity: 0.9;
  max-width: 800px;
  margin: 0 auto;
}

.search-wrapper {
  margin: -35px auto 40px;
  max-width: 700px;
  position: relative;
  z-index: 10;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 50px 0 0 50px;
  padding-left: 20px;
}

.search-input :deep(.el-input-group__append) {
  border-radius: 0 50px 50px 0;
  background: transparent;
}

.search-input :deep(.el-input-group__append button) {
  border-radius: 0 50px 50px 0;
  padding: 0 25px;
}

.major-grid {
  margin-bottom: 40px;
}

.major-card {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  border-radius: 16px;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.major-card:hover {
  transform: translateY(-5px);
}

.card-header {
  padding: 20px 20px 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}

.title-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.title-wrapper h3 {
  font-size: 1.2rem;
  margin: 0;
  color: #333;
}

.arrow {
  color: #667eea;
  font-size: 1.2rem;
  opacity: 0.5;
  transition: opacity 0.3s;
}

.major-card:hover .arrow {
  opacity: 1;
}

.card-body {
  padding: 15px 20px;
  flex: 1;
}

.major-desc {
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
  font-size: 0.95rem;
  min-height: 3.2em;
}

.major-meta {
  display: flex;
  gap: 20px;
  font-size: 0.9rem;
  color: #888;
}

.major-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.major-meta i {
  color: #667eea;
  width: 16px;
}

.card-footer {
  padding: 15px 20px;
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

@media (max-width: 768px) {
  .hero-section {
    padding: 40px 20px;
  }
  .hero-content h1 {
    font-size: 2rem;
  }
  .search-wrapper {
    margin-top: -20px;
  }
  .major-card .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>