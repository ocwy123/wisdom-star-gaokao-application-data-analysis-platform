<template>
  <div>
    <h2>高校列表（来自MySQL）</h2>
    <ul>
      <li v-for="school in schoolList" :key="school.id">
        {{ school.name }} - {{ school.province }}
      </li>
    </ul>

    <h2>高校热度排行（来自Hive）</h2>
    <ul>
      <li v-for="item in heatList" :key="item.school_id">
        {{ item.school_name }} - 热度：{{ item.heat_score }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSchoolList } from '../api/school'
import { getSchoolHeat } from '../api/heat'

const schoolList = ref([])
const heatList = ref([])

onMounted(async () => {
  try {
    const schoolRes = await getSchoolList({ page: 1, size: 10 })
    schoolList.value = schoolRes.data.list

    const heatRes = await getSchoolHeat()
    heatList.value = heatRes.data
  } catch (error) {
    console.error('加载失败', error)
  }
})
</script>