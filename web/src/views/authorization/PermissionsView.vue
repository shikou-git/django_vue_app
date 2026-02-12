<script setup>
import { getPermissionFilterOptions, getPermissionList } from '@/api/auth'
import { SEARCH_DEBOUNCE_MS } from '@/utils/const'
import { SearchOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { computed, onMounted, reactive, ref, watch } from 'vue'

// 表格 body 最大高度，超出出现垂直滚动条（预留顶部、筛选、分页等空间，保证分页可见）
const tableScrollY = ref('calc(100vh - 380px)')

const loading = ref(false)
const searchText = ref('')
const tableFilters = ref({})
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })
const dataSource = ref([])
const appLabelOptions = ref([])
const modelOptions = ref([])
// 排序：{ columnKey: 'app_label', order: 'ascend' | 'descend' } 或 undefined
const sorterState = ref(null)

const columns = computed(() => [
  {
    title: 'App Label',
    dataIndex: 'app_label',
    key: 'app_label',
    width: 140,
    sorter: true,
    filters: appLabelOptions.value.map((v) => ({ text: v, value: v })),
    filteredValue: tableFilters.value.app_label,
  },
  {
    title: 'Model',
    dataIndex: 'model',
    key: 'model',
    width: 140,
    sorter: true,
    filters: modelOptions.value.map((v) => ({ text: v, value: v })),
    filteredValue: tableFilters.value.model,
  },
  { title: 'Codename', dataIndex: 'codename', key: 'codename', width: 180, sorter: true },
  { title: 'Name', dataIndex: 'name', key: 'name', ellipsis: true },
])

const buildOrderBy = () => {
  if (!sorterState.value || !sorterState.value.columnKey || !sorterState.value.order)
    return undefined
  const key = sorterState.value.columnKey
  const dir = sorterState.value.order === 'ascend' ? key : `-${key}`
  return [dir]
}

const toArr = (v) => (Array.isArray(v) && v.length ? v : undefined)

const loadFilterOptions = async () => {
  try {
    const res = await getPermissionFilterOptions()
    const d = res.data || {}
    appLabelOptions.value = d.app_labels || []
    modelOptions.value = d.models || []
  } catch (e) {
    console.error(e)
  }
}

const loadList = async () => {
  loading.value = true
  try {
    const f = tableFilters.value
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      search: searchText.value || undefined,
      app_label: toArr(f.app_label),
      model: toArr(f.model),
      order_by: buildOrderBy(),
    }
    const res = await getPermissionList(params)
    const d = res.data || {}
    dataSource.value = (d.results || []).map((r) => ({ ...r, key: r.id }))
    pagination.total = d.total ?? 0
  } catch (e) {
    message.error(e.message || '加载权限列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadFilterOptions()
  loadList()
})

watch([() => pagination.current, () => pagination.pageSize], () => loadList())

let searchDebounceTimer = null
watch(searchText, () => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    pagination.current = 1
    loadList()
    searchDebounceTimer = null
  }, SEARCH_DEBOUNCE_MS)
})

const handleTableChange = (pag, filters, sorter) => {
  const filtersChanged = JSON.stringify(tableFilters.value) !== JSON.stringify(filters)
  tableFilters.value = filters
  pagination.pageSize = pag.pageSize
  pagination.current = filtersChanged ? 1 : pag.current
  sorterState.value =
    sorter && (sorter.order === 'ascend' || sorter.order === 'descend')
      ? { columnKey: sorter.columnKey, order: sorter.order }
      : null
  loadList()
}
</script>

<template>
  <div class="permissions-view">
    <a-page-header title="权限管理" sub-title="" style="padding: 0 0 24px 0" />

    <a-card :bordered="false">
      <div class="filter-toolbar">
        <a-input
          v-model:value="searchText"
          placeholder="搜索 App、Model、Codename、Name"
          class="filter-toolbar__search"
          allow-clear
        >
          <template #prefix><SearchOutlined /></template>
        </a-input>
      </div>

      <a-table
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: pagination.total,
          showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条`,
        }"
        :scroll="{ x: 600, y: tableScrollY }"
        @change="handleTableChange"
      />
    </a-card>
  </div>
</template>

<style scoped>
.permissions-view {
  width: 100%;
}

.filter-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  width: 100%;
}

.filter-toolbar__search {
  width: 320px;
}
</style>
