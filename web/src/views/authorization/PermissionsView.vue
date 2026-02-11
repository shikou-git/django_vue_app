<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons-vue'
import { message, Modal } from 'ant-design-vue'
import {
  getPermissionList,
  getPermissionDetail,
  createPermission,
  updatePermission,
  deletePermission,
} from '@/api/auth'

const loading = ref(false)
const searchText = ref('')
const contentTypeFilter = ref(undefined)
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })
const dataSource = ref([])
const contentTypes = ref([])

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '权限名称', dataIndex: 'name', key: 'name', ellipsis: true },
  { title: 'Codename', dataIndex: 'codename', key: 'codename', width: 180 },
  { title: '内容类型', dataIndex: 'content_type_name', key: 'content_type_name', width: 120 },
  { title: 'Content Type ID', dataIndex: 'content_type', key: 'content_type', width: 120 },
  { title: '操作', key: 'action', width: 140, fixed: 'right' },
]

const loadList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      search: searchText.value || undefined,
      content_type: contentTypeFilter.value,
    }
    const res = await getPermissionList(params)
    const d = res.data || {}
    dataSource.value = (d.results || []).map((r) => ({ ...r, key: r.id }))
    pagination.total = d.total ?? 0
    if (contentTypes.value.length === 0 && dataSource.value.length > 0) {
      const set = new Map()
      dataSource.value.forEach((p) => {
        if (p.content_type != null && p.content_type_name) {
          set.set(p.content_type, { id: p.content_type, name: p.content_type_name })
        }
      })
      contentTypes.value = Array.from(set.values())
    }
  } catch (e) {
    message.error(e.message || '加载权限列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => loadList())

watch([() => pagination.current, () => pagination.pageSize], () => loadList())

const handleSearch = () => loadList()

const modalVisible = ref(false)
const modalLoading = ref(false)
const isEdit = ref(false)
const formState = reactive({
  permission_id: null,
  name: '',
  codename: '',
  content_type_id: undefined,
})

const openCreate = () => {
  isEdit.value = false
  formState.permission_id = null
  formState.name = ''
  formState.codename = ''
  formState.content_type_id = undefined
  modalVisible.value = true
}

const openEdit = async (record) => {
  isEdit.value = true
  try {
    const res = await getPermissionDetail({ permission_id: record.id })
    const p = res.data || {}
    formState.permission_id = p.id
    formState.name = p.name || ''
    formState.codename = p.codename || ''
    formState.content_type_id = p.content_type
    modalVisible.value = true
  } catch (e) {
    message.error(e.message || '获取权限详情失败')
  }
}

const handleModalOk = async () => {
  if (!formState.name.trim()) {
    message.warning('请输入权限名称')
    return
  }
  if (!formState.codename.trim()) {
    message.warning('请输入 codename')
    return
  }
  if (!isEdit.value && (formState.content_type_id == null || formState.content_type_id === '')) {
    message.warning('请输入内容类型 ID（创建自定义权限需在 Django 后台查看 ContentType ID）')
    return
  }
  modalLoading.value = true
  try {
    if (isEdit.value) {
      await updatePermission({
        permission_id: formState.permission_id,
        name: formState.name.trim(),
        codename: formState.codename.trim(),
      })
      message.success('更新成功')
    } else {
      await createPermission({
        content_type_id: formState.content_type_id,
        name: formState.name.trim(),
        codename: formState.codename.trim(),
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

const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除权限「${record.name}」吗？`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await deletePermission({ permission_id: record.id })
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
  <div class="permissions-view">
    <a-page-header title="权限管理" sub-title="查看与维护系统权限" style="padding: 0 0 24px 0">
      <template #extra>
        <a-button type="primary" @click="openCreate">
          <template #icon><PlusOutlined /></template>
          新建权限
        </a-button>
      </template>
    </a-page-header>

    <a-card :bordered="false">
      <a-space style="margin-bottom: 16px" :size="12">
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索权限名称、codename..."
          enter-button
          style="width: 260px"
          allow-clear
          @search="handleSearch"
        >
          <template #prefix><SearchOutlined /></template>
        </a-input-search>
        <a-select
          v-model:value="contentTypeFilter"
          placeholder="内容类型"
          style="width: 140px"
          allow-clear
          @change="handleSearch"
        >
          <a-select-option v-for="ct in contentTypes" :key="ct.id" :value="ct.id">{{ ct.name }}</a-select-option>
        </a-select>
        <a-button type="primary" @click="handleSearch">查询</a-button>
      </a-space>

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
        :scroll="{ x: 900 }"
        @change="(pag) => { pagination.current = pag.current; pagination.pageSize = pag.pageSize }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="openEdit(record)">编辑</a-button>
              <a-button type="link" danger size="small" @click="handleDelete(record)">删除</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑权限' : '新建权限'"
      :confirm-loading="modalLoading"
      ok-text="保存"
      @ok="handleModalOk"
    >
      <a-form layout="vertical">
        <a-form-item label="权限名称" required>
          <a-input v-model:value="formState.name" placeholder="如：导出用户" />
        </a-form-item>
        <a-form-item label="Codename" required>
          <a-input v-model:value="formState.codename" placeholder="如：export_user" :disabled="isEdit" />
        </a-form-item>
        <a-form-item v-if="!isEdit" label="内容类型 ID" required>
          <a-input-number
            v-model:value="formState.content_type_id"
            placeholder="如 4 表示 User 模型"
            style="width: 100%"
            :min="1"
          />
          <div style="color: #999; font-size: 12px; margin-top: 4px">
            可在权限列表中查看已有权限的 content_type，或到 Django 后台查看 Content type。
          </div>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<style scoped>
.permissions-view {
  max-width: 1200px;
}
</style>
