<script setup>
import {
  createGroup,
  deleteGroup,
  getGroupDetail,
  getGroupList,
  getPermissionList,
  updateGroup,
} from '@/api/auth'
import { SEARCH_DEBOUNCE_MS } from '@/utils/const'
import { SearchOutlined, UserAddOutlined } from '@ant-design/icons-vue'
import { message, Modal } from 'ant-design-vue'
import { computed, onMounted, reactive, ref, watch } from 'vue'

// 表格 body 最大高度，超出出现垂直滚动条（预留顶部、筛选、分页等空间，保证分页可见）
const tableScrollY = ref('calc(100vh - 380px)')

const loading = ref(false)
const searchText = ref('')
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })
const dataSource = ref([])

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '角色名称', dataIndex: 'name', key: 'name', width: 180 },
  { title: '用户数', dataIndex: 'user_count', key: 'user_count', width: 100 },
  { title: '权限数', dataIndex: 'permission_count', key: 'permission_count', width: 100 },
  { title: '操作', key: 'action', width: 160, fixed: 'right' },
]

const loadList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      search: searchText.value || undefined,
    }
    const res = await getGroupList(params)
    const d = res.data || {}
    dataSource.value = (d.results || []).map((r) => ({ ...r, key: r.id }))
    pagination.total = d.total ?? 0
  } catch (e) {
    message.error(e.message || '加载角色列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => loadList())

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

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadList()
}

// ---------- 新建/编辑 ----------
const modalVisible = ref(false)
const modalLoading = ref(false)
const isEdit = ref(false)
const formState = reactive({
  group_id: null,
  name: '',
  permission_ids: [],
})

// 权限选择表格：与权限管理同结构，勾选即选中
const permissionTableLoading = ref(false)
const permissionListAll = ref([])
const permissionSearch = ref('')

// 弹窗内权限表格：列宽根据内容自适应
const permissionTableColumns = [
  { title: 'App', dataIndex: 'app_label', key: 'app_label' },
  { title: 'Model', dataIndex: 'model', key: 'model' },
  { title: 'Codename', dataIndex: 'codename', key: 'codename' },
  { title: 'Name', dataIndex: 'name', key: 'name', ellipsis: true },
]

const permissionTableData = computed(() => {
  const list = permissionListAll.value
  const q = (permissionSearch.value || '').trim().toLowerCase()
  if (!q) return list.map((r) => ({ ...r, key: r.id }))
  return list
    .filter(
      (p) =>
        (p.app_label || '').toLowerCase().includes(q) ||
        (p.model || '').toLowerCase().includes(q) ||
        (p.codename || '').toLowerCase().includes(q) ||
        (p.name || '').toLowerCase().includes(q),
    )
    .map((r) => ({ ...r, key: r.id }))
})

const permissionRowSelection = computed(() => ({
  selectedRowKeys: formState.permission_ids,
  onChange: (keys) => {
    formState.permission_ids = keys
  },
}))

const loadPermissionList = async () => {
  permissionTableLoading.value = true
  try {
    const res = await getPermissionList({ page: 1, page_size: 2000 })
    permissionListAll.value = res.data?.results || []
  } catch (e) {
    console.error(e)
    permissionListAll.value = []
  } finally {
    permissionTableLoading.value = false
  }
}

const openCreate = () => {
  isEdit.value = false
  formState.group_id = null
  formState.name = ''
  formState.permission_ids = []
  permissionSearch.value = ''
  loadPermissionList()
  modalVisible.value = true
}

const openEdit = async (record) => {
  isEdit.value = true
  modalLoading.value = true
  try {
    const [detailRes, _] = await Promise.all([
      getGroupDetail({ group_id: record.id }),
      loadPermissionList(),
    ])
    const g = detailRes.data || {}
    formState.group_id = g.id
    formState.name = g.name || ''
    formState.permission_ids = g.permission_ids || []
    permissionSearch.value = ''
    modalVisible.value = true
  } catch (e) {
    message.error(e.message || '获取角色详情失败')
  } finally {
    modalLoading.value = false
  }
}

const handleModalOk = async () => {
  const name = (formState.name || '').trim()
  if (!name) {
    message.warning('请输入角色名称')
    return
  }
  modalLoading.value = true
  try {
    if (isEdit.value) {
      await updateGroup({
        group_id: formState.group_id,
        name,
        permission_ids: formState.permission_ids,
      })
      message.success('更新成功')
    } else {
      await createGroup({
        name,
        permission_ids: formState.permission_ids,
      })
      message.success('创建成功')
    }
    modalVisible.value = false
    loadList()
  } catch (e) {
    message.error(e.message || '保存失败')
  } finally {
    modalLoading.value = false
  }
}

// ---------- 删除 ----------
const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除角色「${record.name}」吗？该角色下的用户将失去此角色。`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await deleteGroup({ group_id: record.id })
        message.success('已删除')
        loadList()
      } catch (e) {
        message.error(e.message || '删除失败')
      }
    },
  })
}
</script>

<template>
  <div class="roles-view">
    <a-page-header title="角色管理" sub-title="" style="padding: 0 0 24px 0">
      <template #extra>
        <a-button type="primary" @click="openCreate">
          <template #icon><UserAddOutlined /></template>
          添加角色
        </a-button>
      </template>
    </a-page-header>

    <a-card :bordered="false">
      <div class="filter-toolbar">
        <a-input
          v-model:value="searchText"
          placeholder="搜索角色名称"
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
        :scroll="{ x: 620, y: tableScrollY }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="openEdit(record)">编辑</a-button>
              <a-button type="link" danger size="small" @click="handleDelete(record)"
                >删除</a-button
              >
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑角色' : '新建角色'"
      :confirm-loading="modalLoading"
      ok-text="保存"
      width="420"
      @ok="handleModalOk"
    >
      <a-form layout="vertical">
        <a-form-item label="角色名称" required>
          <a-input v-model:value="formState.name" placeholder="角色名称" class="role-name-input" />
        </a-form-item>
        <a-form-item label="权限（勾选表格行即可选择）">
          <a-input
            v-model:value="permissionSearch"
            placeholder="搜索 App、Model、Codename、Name"
            allow-clear
            class="permission-table-search"
          >
            <template #prefix><SearchOutlined /></template>
          </a-input>
          <a-table
            :columns="permissionTableColumns"
            :data-source="permissionTableData"
            :loading="permissionTableLoading"
            :row-selection="permissionRowSelection"
            :scroll="{ y: 280 }"
            :pagination="false"
            size="small"
            class="permission-select-table"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<style scoped>
.roles-view {
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
  width: 200px;
}

.role-name-input {
  width: 240px;
}

.permission-table-search {
  margin-bottom: 8px;
  width: 320px;
}

.permission-select-table {
  margin-top: 0;
  max-width: 100%;
}
.permission-select-table :deep(.ant-table-wrapper),
.permission-select-table :deep(.ant-spin-nested-loading),
.permission-select-table :deep(.ant-table) {
  max-width: 100%;
}
.permission-select-table :deep(.ant-table) {
  font-size: 13px;
}
</style>
