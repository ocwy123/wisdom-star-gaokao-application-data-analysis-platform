<template>
  <div class="chart-view">
    <el-row :gutter="20">
      <el-col :span="12" v-for="chart in charts" :key="chart.title">
        <el-card>
          <template #header>
            <span>{{ chart.title }}</span>
          </template>
          <div :ref="chart.ref" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'ChartView',
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      charts: [
        { title: '热度分布', ref: 'heatChart' },
        { title: '分数分布', ref: 'scoreChart' }
      ],
      chartInstances: {}
    }
  },
  watch: {
    data: {
      handler() {
        this.$nextTick(() => {
          this.initCharts()
        })
      },
      deep: true
    }
  },
  mounted() {
    this.initCharts()
  },
  methods: {
    initCharts() {
      if (this.data.length === 0) return
      
      // 热度分布图
      if (this.$refs.heatChart) {
        if (this.chartInstances.heatChart) {
          this.chartInstances.heatChart.dispose()
        }
        const heatChart = echarts.init(this.$refs.heatChart[0])
        heatChart.setOption({
          tooltip: { trigger: 'axis' },
          xAxis: {
            type: 'category',
            data: this.data.slice(0, 10).map(item => 
              item.name || item.school_name || item.major_name
            )
          },
          yAxis: { type: 'value' },
          series: [{
            data: this.data.slice(0, 10).map(item => item.heat_score || 0),
            type: 'bar',
            name: '热度'
          }]
        })
        this.chartInstances.heatChart = heatChart
      }
      
      // 分数分布图
      if (this.$refs.scoreChart) {
        if (this.chartInstances.scoreChart) {
          this.chartInstances.scoreChart.dispose()
        }
        const scoreChart = echarts.init(this.$refs.scoreChart[0])
        scoreChart.setOption({
          tooltip: { trigger: 'axis' },
          xAxis: {
            type: 'category',
            data: this.data.slice(0, 10).map(item => 
              item.name || item.school_name || item.major_name
            )
          },
          yAxis: { type: 'value' },
          series: [{
            data: this.data.slice(0, 10).map(item => item.min_score || 0),
            type: 'line',
            name: '最低分数'
          }]
        })
        this.chartInstances.scoreChart = scoreChart
      }
    }
  }
}
</script>