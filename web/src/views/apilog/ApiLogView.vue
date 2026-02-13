<script setup>
import {
  batchDeleteApilog,
  deleteApilog,
  exportApilog,
  getApilogList,
  getFilterOptions,
} from '@/api/apilog'
import { useTableMultiSelectFilter } from '@/components/table/useTableMultiSelectFilter'
import { useAuthStore } from '@/stores/auth'
import { DeleteOutlined, DownloadOutlined } from '@ant-design/icons-vue'
import { message, Modal } from 'ant-design-vue'
import dayjs from 'dayjs'
import { computed, onMounted, reactive, ref } from 'vue'

const authStore = useAuthStore()
const canExport = computed(
  () =>
    authStore.user?.is_superuser === true ||
    (authStore.user?.permissions || []).includes('apilog.export_apilog'),
)
const canDelete = computed(
  () =>
    authStore.user?.is_superuser === true ||
    (authStore.user?.permissions || []).includes('apilog.delete_apilog'),
)

const tableScrollY = ref('calc(100vh - 380px)')
const loading = ref(false)
const exportLoading = ref(false)
const tableFilters = ref({})
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })
const dataSource = ref([])
const sorterState = ref(null)
const selectedRowKeys = ref([])

// 仅时间范围放在工具栏
const timeRange = reactive({
  created_at_start: undefined,
  created_at_end: undefined,
})

const buildOrderBy = () => {
  if (!sorterState.value?.columnKey || !sorterState.value?.order) return undefined
  const key = sorterState.value.columnKey
  const dir = sorterState.value.order === 'ascend' ? key : `-${key}`
  return [dir]
}

const toVal = (v) => (v !== undefined && v !== null && v !== '' ? v : undefined)
const toFilterVal = (v) => {
  if (v === undefined || v === null) return undefined
  if (Array.isArray(v) && v.length) return v
  return v
}

const {
  filterOptionsCache,
  loadFilterOptions,
  renderMultiSelectFilterDropdown,
} = useTableMultiSelectFilter(async (columnKey, search) => {
  const res = await getFilterOptions({ field: columnKey, search })
  return res.data?.options || []
})

const columns = computed(() => [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
  {
    title: '路径',
    dataIndex: 'path',
    key: 'path',
    width: 220,
    ellipsis: true,
    filterDropdown: renderMultiSelectFilterDropdown({ columnKey: 'path', placeholder: '路径' }),
    filteredValue: tableFilters.value.path,
    onFilterDropdownOpenChange: (open) => {
      if (open && !filterOptionsCache.path?.length) loadFilterOptions('path')
    },
  },
  {
    title: '方法',
    dataIndex: 'method',
    key: 'method',
    width: 90,
  },
  {
    title: '状态码',
    dataIndex: 'status_code',
    key: 'status_code',
    width: 90,
    filterDropdown: renderMultiSelectFilterDropdown({
      columnKey: 'status_code',
      placeholder: '状态码',
    }),
    filteredValue: tableFilters.value.status_code,
    onFilterDropdownOpenChange: (open) => {
      if (open && !filterOptionsCache.status_code?.length) loadFilterOptions('status_code')
    },
  },
  {
    title: '用户ID',
    dataIndex: 'user_id',
    key: 'user_id',
    width: 90,
    filterDropdown: renderMultiSelectFilterDropdown({
      columnKey: 'user_id',
      placeholder: '用户ID',
    }),
    filteredValue: tableFilters.value.user_id,
    onFilterDropdownOpenChange: (open) => {
      if (open && !filterOptionsCache.user_id?.length) loadFilterOptions('user_id')
    },
  },
  {
    title: 'IP',
    dataIndex: 'ip_address',
    key: 'ip_address',
    width: 130,
    ellipsis: true,
    filterDropdown: renderMultiSelectFilterDropdown({ columnKey: 'ip_address', placeholder: 'IP' }),
    filteredValue: tableFilters.value.ip_address,
    onFilterDropdownOpenChange: (open) => {
      if (open && !filterOptionsCache.ip_address?.length) loadFilterOptions('ip_address')
    },
  },
  { title: 'User-Agent', dataIndex: 'user_agent', key: 'user_agent', width: 200, ellipsis: true },
  {
    title: '时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 170,
    sorter: true,
    sortOrder: sorterState.value?.columnKey === 'created_at' ? sorterState.value.order : undefined,
  },
  { title: '操作', key: 'action', width: 90, fixed: 'right' },
])

const rowSelection = computed(() => ({
  selectedRowKeys: selectedRowKeys.value,
  onChange: (keys) => {
    selectedRowKeys.value = keys
  },
}))

const loadList = async () => {
  loading.value = true
  try {
    const f = tableFilters.value
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      path: toVal(toFilterVal(f.path)),
      status_code: toVal(toFilterVal(f.status_code)),
      user_id: toVal(toFilterVal(f.user_id)),
      ip_address: toVal(toFilterVal(f.ip_address)),
      created_at_start:
        timeRange.created_at_start && dayjs(timeRange.created_at_start).isValid()
          ? dayjs(timeRange.created_at_start).format('YYYY-MM-DD HH:mm:ss')
          : undefined,
      created_at_end:
        timeRange.created_at_end && dayjs(timeRange.created_at_end).isValid()
          ? dayjs(timeRange.created_at_end).format('YYYY-MM-DD HH:mm:ss')
          : undefined,
      order_by: buildOrderBy(),
    }
    const res = await getApilogList(params)
    const d = res.data || {}
    dataSource.value = (d.results || []).map((r) => ({ ...r, key: r.id }))
    pagination.total = d.total ?? 0
  } catch (e) {
    message.error(e.message || '加载接口日志失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadList()
}

const handleResetFilters = () => {
  tableFilters.value = {}
  timeRange.created_at_start = undefined
  timeRange.created_at_end = undefined
  pagination.current = 1
  loadList()
}

onMounted(() => {
  loadList()
})

const handleTableChange = (pag, filters, sorter) => {
  const filtersChanged = JSON.stringify(tableFilters.value) !== JSON.stringify(filters)
  tableFilters.value = filters
  pagination.pageSize = pag.pageSize
  pagination.current = filtersChanged ? 1 : pag.current
  sorterState.value =
    sorter?.columnKey && (sorter.order === 'ascend' || sorter.order === 'descend')
      ? { columnKey: sorter.columnKey, order: sorter.order }
      : null
  loadList()
}

const handleExport = async () => {
  if (!canExport.value) {
    message.warning('无导出权限')
    return
  }
  exportLoading.value = true
  try {
    const f = tableFilters.value
    const params = {
      path: toVal(toFilterVal(f.path)),
      status_code: toVal(toFilterVal(f.status_code)),
      user_id: toVal(toFilterVal(f.user_id)),
      ip_address: toVal(toFilterVal(f.ip_address)),
      created_at_start:
        timeRange.created_at_start && dayjs(timeRange.created_at_start).isValid()
          ? dayjs(timeRange.created_at_start).format('YYYY-MM-DD HH:mm:ss')
          : undefined,
      created_at_end:
        timeRange.created_at_end && dayjs(timeRange.created_at_end).isValid()
          ? dayjs(timeRange.created_at_end).format('YYYY-MM-DD HH:mm:ss')
          : undefined,
    }
    const res = await exportApilog(params)
    const contentType = res.headers['content-type'] || ''
    if (contentType.indexOf('application/json') !== -1) {
      const text = await res.data.text()
      const body = JSON.parse(text)
      throw new Error(body.msg || '导出失败')
    }
    const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const disp = res.headers['content-disposition']
    const match = disp && disp.match(/filename="?([^";]+)"?/)
    link.download = match ? match[1].trim() : `api_log_${Date.now()}.csv`
    link.click()
    URL.revokeObjectURL(url)
    message.success('导出成功')
  } catch (e) {
    message.error(e.message || '导出失败')
  } finally {
    exportLoading.value = false
  }
}

const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除该条日志吗？路径：${(record.path || '').slice(0, 50)}${(record.path || '').length > 50 ? '…' : ''}`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await deleteApilog({ id: record.id })
        message.success('已删除')
        loadList()
      } catch (e) {
        message.error(e.message || '删除失败')
      }
    },
  })
}

const handleBatchDelete = () => {
  if (!selectedRowKeys.value.length) {
    message.warning('请先勾选要删除的日志')
    return
  }
  Modal.confirm({
    title: '确认批量删除',
    content: `确定要删除选中的 ${selectedRowKeys.value.length} 条日志吗？`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await batchDeleteApilog({ ids: selectedRowKeys.value })
        message.success('已删除')
        selectedRowKeys.value = []
        loadList()
      } catch (e) {
        message.error(e.message || '删除失败')
      }
    },
  })
}
</script>

<template>
  <div class="apilog-view">
    <a-page-header title="接口日志" sub-title="" style="padding: 0 0 24px 0">
      <template #extra>
        <a-button
          danger
          :disabled="!canDelete || !selectedRowKeys.length"
          @click="handleBatchDelete"
        >
          <template #icon><DeleteOutlined /></template>
          批量删除
        </a-button>
        <a-button
          type="primary"
          :loading="exportLoading"
          :disabled="!canExport"
          @click="handleExport"
        >
          <template #icon><DownloadOutlined /></template>
          导出 CSV
        </a-button>
      </template>
    </a-page-header>

    <a-card :bordered="false">
      <div class="filter-toolbar">
        <a-date-picker
          v-model:value="timeRange.created_at_start"
          show-time
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
          placeholder="开始时间"
          class="filter-toolbar__date"
        />
        <span class="filter-toolbar__sep">至</span>
        <a-date-picker
          v-model:value="timeRange.created_at_end"
          show-time
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
          placeholder="结束时间"
          class="filter-toolbar__date"
        />
        <a-button type="primary" @click="handleSearch">查询</a-button>
        <a-button @click="handleResetFilters">重置</a-button>
      </div>

      <a-table
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :row-selection="canDelete ? rowSelection : undefined"
        :pagination="{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: pagination.total,
          showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条`,
        }"
        :scroll="{ x: 1300, y: tableScrollY }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-button
              v-if="canDelete"
              type="link"
              danger
              size="small"
              @click="handleDelete(record)"
            >
              删除
            </a-button>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<style scoped>
.apilog-view {
  width: 100%;
}

.apilog-view :deep(.ant-table-thead th),
.apilog-view :deep(.ant-table-thead th .ant-table-column-title) {
  font-weight: 600;
}

.filter-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  width: 100%;
}

.filter-toolbar__date {
  width: 180px;
}

.apilog-view :deep(.table-multi-select-filter-dropdown) {
  min-width: 200px;
}

.filter-toolbar__sep {
  color: rgba(0, 0, 0, 0.45);
  padding: 0 4px;
}
</style>
