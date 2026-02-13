<script setup>
import { getApiStats } from '@/api/apilog'
import dayjs from 'dayjs'
import { BarChart } from 'echarts/charts'
import { GridComponent, TitleComponent, TooltipComponent } from 'echarts/components'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { computed, onMounted, ref, watch } from 'vue'
import VChart from 'vue-echarts'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, TitleComponent])

const filterType = ref('month')
const year = ref(dayjs().year())
const month = ref(dayjs().month() + 1)
const dayDate = ref(dayjs().format('YYYY-MM-DD'))
const dateRange = ref([
  dayjs().startOf('month').format('YYYY-MM-DD'),
  dayjs().endOf('month').format('YYYY-MM-DD'),
])

const loading = ref(false)
const apiRanking = ref([])
const userRanking = ref([])

const yearOptions = computed(() => {
  const y = dayjs().year()
  return Array.from({ length: 5 }, (_, i) => y - 2 + i)
})

const monthOptions = Array.from({ length: 12 }, (_, i) => ({ value: i + 1, label: `${i + 1} 月` }))

const requestPayload = computed(() => {
  const payload = { filter_type: filterType.value }
  if (filterType.value === 'year') {
    payload.year = year.value
  } else if (filterType.value === 'month') {
    payload.year = year.value
    payload.month = month.value
  } else if (filterType.value === 'day' && dayDate.value) {
    const d = dayjs(dayDate.value)
    payload.year = d.year()
    payload.month = d.month() + 1
    payload.day = d.date()
  } else if (filterType.value === 'range' && dateRange.value?.length === 2) {
    payload.date_start = dayjs(dateRange.value[0]).format('YYYY-MM-DD')
    payload.date_end = dayjs(dateRange.value[1]).format('YYYY-MM-DD')
  }
  return payload
})

async function loadStats() {
  if (filterType.value === 'range' && dateRange.value?.length !== 2) return
  if (filterType.value === 'day' && !dayDate.value) return
  loading.value = true
  try {
    const res = await getApiStats(requestPayload.value)
    apiRanking.value = res.data?.api_ranking ?? []
    userRanking.value = res.data?.user_ranking ?? []
  } finally {
    loading.value = false
  }
}

const apiChartOption = computed(() => {
  const list = apiRanking.value
  const labels = list.map((r) => (r.path || '').trim() || '(空)').reverse()
  return {
    title: { text: 'Top 接口调用量排行', left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: { left: 20, right: 150, top: 36, bottom: 24, containLabel: true },
    xAxis: { type: 'value', name: '调用次数', nameGap: 8 },
    yAxis: {
      name: '接口路径',
      type: 'category',
      data: labels,
      axisLabel: { show: false },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [
      {
        type: 'bar',
        data: list.map((r) => r.count).reverse(),
        itemStyle: { color: '#1890ff' },
        label: {
          show: true,
          position: 'insideRight',
          color: '#fff',
          padding: [0, 2, 0, 0],
          formatter: ({ value }) => value,
        },
      },
      {
        type: 'bar',
        data: list.map((r) => r.count).reverse(),
        barGap: '-100%',
        itemStyle: { color: 'transparent' },
        emphasis: { itemStyle: { color: 'transparent' } },
        label: {
          show: true,
          position: 'right',
          color: 'rgba(0,0,0,0.85)',
          padding: [0, 0, 0, 2],
          overflow: 'truncate',
          width: 200,
          formatter: ({ dataIndex }) => labels[dataIndex] || '',
        },
      },
    ],
  }
})

const userChartOption = computed(() => {
  const list = userRanking.value
  const labels = list.map((r) => r.username || '匿名').reverse()
  return {
    title: { text: 'Top 用户调用量排行', left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: { left: 20, right: 100, top: 36, bottom: 24, containLabel: true },
    xAxis: { type: 'value', name: '调用次数', nameGap: 8 },
    yAxis: {
      name: '用户名',
      type: 'category',
      data: labels,
      axisLabel: { show: false },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [
      {
        type: 'bar',
        data: list.map((r) => r.count).reverse(),
        itemStyle: { color: '#52c41a' },
        label: {
          show: true,
          position: 'insideRight',
          color: '#fff',
          padding: [0, 2, 0, 0],
          formatter: ({ value }) => value,
        },
      },
      {
        type: 'bar',
        data: list.map((r) => r.count).reverse(),
        barGap: '-100%',
        itemStyle: { color: 'transparent' },
        emphasis: { itemStyle: { color: 'transparent' } },
        label: {
          show: true,
          position: 'right',
          color: 'rgba(0,0,0,0.85)',
          padding: [0, 0, 0, 2],
          overflow: 'truncate',
          width: 80,
          formatter: ({ dataIndex }) => labels[dataIndex] || '',
        },
      },
    ],
  }
})

onMounted(loadStats)
watch([filterType, year, month, dayDate, dateRange], loadStats, { deep: true })
</script>

<template>
  <div class="api-stats-view">
    <div class="filter-bar">
      <a-space wrap>
        <span>筛选：</span>
        <a-radio-group v-model:value="filterType" button-style="solid">
          <a-radio-button value="year">年</a-radio-button>
          <a-radio-button value="month">月</a-radio-button>
          <a-radio-button value="day">日</a-radio-button>
          <a-radio-button value="range">日期段</a-radio-button>
        </a-radio-group>
        <template v-if="filterType === 'year'">
          <a-select
            v-model:value="year"
            style="width: 100px"
            :options="yearOptions.map((y) => ({ value: y, label: `${y} 年` }))"
          />
        </template>
        <template v-else-if="filterType === 'month'">
          <a-select
            v-model:value="year"
            style="width: 100px"
            :options="yearOptions.map((y) => ({ value: y, label: `${y} 年` }))"
          />
          <a-select v-model:value="month" style="width: 100px" :options="monthOptions" />
        </template>
        <template v-else-if="filterType === 'day'">
          <a-date-picker
            v-model:value="dayDate"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 140px"
          />
        </template>
        <template v-else-if="filterType === 'range'">
          <a-range-picker
            v-model:value="dateRange"
            value-format="YYYY-MM-DD"
            style="width: 240px"
          />
        </template>
        <a-button type="primary" :loading="loading" @click="loadStats">查询</a-button>
      </a-space>
    </div>
    <a-spin :spinning="loading">
      <div class="charts">
        <div class="chart-card">
          <v-chart class="chart" :option="apiChartOption" autoresize />
        </div>
        <div class="chart-card">
          <v-chart class="chart" :option="userChartOption" autoresize />
        </div>
      </div>
    </a-spin>
  </div>
</template>

<style scoped>
.api-stats-view {
  padding: 16px;
}
.filter-bar {
  margin-bottom: 20px;
}
.charts {
  display: flex;
  flex-direction: row;
  gap: 24px;
}
.chart-card {
  flex: 1;
  min-width: 0;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}
.chart {
  height: 380px;
  width: 100%;
}
@media (max-width: 900px) {
  .charts {
    flex-direction: column;
  }
}
</style>
