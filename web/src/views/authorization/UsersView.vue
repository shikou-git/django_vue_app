<script setup>
import {
  createUser,
  deleteUser,
  getGroupList,
  getUserDetail,
  getUserList,
  resetPassword,
  toggleUserActive,
  updateUser,
} from '@/api/auth'
import { SearchOutlined, UserAddOutlined } from '@ant-design/icons-vue'
import { message, Modal } from 'ant-design-vue'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { DEFAULT_PASSWORD } from '@/utils/const'

const loading = ref(false)
const searchText = ref('')
const tableFilters = ref({})
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })
const dataSource = ref([])
const groupOptions = ref([])

const columns = computed(() => [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
  { title: '工号', dataIndex: 'username', key: 'username', width: 120 },
  { title: '真实姓名', dataIndex: 'real_name', key: 'real_name', width: 120, ellipsis: true },
  {
    title: '角色',
    dataIndex: 'groups',
    key: 'groups',
    width: 150,
    ellipsis: true,
    filters: groupOptions.value.map((g) => ({ text: g.name, value: g.id })),
    filteredValue: tableFilters.value.groups,
  },
  {
    title: '状态',
    dataIndex: 'is_active',
    key: 'is_active',
    width: 90,
    filters: [
      { text: '启用', value: true },
      { text: '禁用', value: false },
    ],
    filteredValue: tableFilters.value.is_active,
  },
  {
    title: '用户类型',
    dataIndex: 'is_superuser',
    key: 'is_superuser',
    width: 130,
    filters: [
      { text: '超级管理员', value: true },
      { text: '普通用户', value: false },
    ],
    filteredValue: tableFilters.value.is_superuser,
  },
  { title: '注册时间', dataIndex: 'date_joined', key: 'date_joined', width: 170 },
  { title: '最后登录时间', dataIndex: 'last_login', key: 'last_login', width: 170 },
  { title: '操作', key: 'action', width: 260, fixed: 'right' },
])

const loadGroups = async () => {
  try {
    const res = await getGroupList()
    groupOptions.value = (res.data && res.data.results) || []
  } catch (e) {
    console.error(e)
  }
}

const loadList = async () => {
  loading.value = true
  try {
    const f = tableFilters.value
    const toArr = (v) => (Array.isArray(v) && v.length ? v : undefined)
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      search: searchText.value || undefined,
      is_active: toArr(f.is_active),
      is_superuser: toArr(f.is_superuser),
      groups: toArr(f.groups),
    }
    const res = await getUserList(params)
    const d = res.data || {}
    dataSource.value = (d.results || []).map((r) => ({ ...r, key: r.id }))
    pagination.total = d.total ?? 0
  } catch (e) {
    message.error(e.message || '加载用户列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadGroups()
  loadList()
})

// 搜索框实时搜索（防抖 300ms）
let searchDebounceTimer = null
watch(searchText, () => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    pagination.current = 1
    loadList()
    searchDebounceTimer = null
  }, 300)
})

const handleTableChange = (pag, filters) => {
  const filtersChanged = JSON.stringify(tableFilters.value) !== JSON.stringify(filters)
  tableFilters.value = filters
  pagination.pageSize = pag.pageSize
  pagination.current = filtersChanged ? 1 : pag.current
  loadList()
}

// ---------- 新建/编辑 用户 ----------
const modalVisible = ref(false)
const modalLoading = ref(false)
const isEdit = ref(false)
const formState = reactive({
  user_id: null,
  username: '',
  password: '',
  real_name: '',
  is_active: true,
  group_ids: [],
})

const openCreate = () => {
  isEdit.value = false
  Object.assign(formState, {
    user_id: null,
    username: '',
    password: '',
    real_name: '',
    is_active: true,
    group_ids: [],
  })
  modalVisible.value = true
}

const openEdit = async (record) => {
  isEdit.value = true
  try {
    const res = await getUserDetail({ user_id: record.id })
    const u = res.data || {}
    Object.assign(formState, {
      user_id: u.id,
      username: u.username,
      password: '',
      real_name: u.real_name || '',
      is_active: u.is_active ?? true,
      group_ids: (u.groups || []).map((g) => g.id),
    })
    modalVisible.value = true
  } catch (e) {
    message.error(e.message || '获取用户详情失败')
  }
}

const handleModalOk = async () => {
  if (!formState.username.trim()) {
    message.warning('请输入工号')
    return
  }
  modalLoading.value = true
  try {
    if (isEdit.value) {
      await updateUser({
        user_id: formState.user_id,
        username: formState.username.trim(),
        real_name: formState.real_name,
        is_active: formState.is_active,
        group_ids: formState.group_ids,
      })
      message.success('更新成功')
    } else {
      await createUser({
        username: formState.username.trim(),
        password: formState.password || DEFAULT_PASSWORD,
        real_name: formState.real_name,
        is_active: formState.is_active,
        group_ids: formState.group_ids,
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
    content: `确定要删除用户「${record.username}」吗？`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await deleteUser({ user_id: record.id })
        message.success('已删除')
        loadList()
      } catch (e) {
        message.error(e.message || '删除失败')
      }
    },
  })
}

// ---------- 重置密码（重置为默认密码） ----------
const handleResetPassword = (record) => {
  Modal.confirm({
    title: '确认重置密码',
    content: `确定将用户「${record.username}」的密码重置为默认密码吗？`,
    okText: '确定',
    cancelText: '取消',
    async onOk() {
      try {
        await resetPassword({ user_id: record.id })
        message.success('密码已重置为默认密码')
      } catch (e) {
        message.error(e.message || '重置失败')
      }
    },
  })
}

// ---------- 启用/禁用 ----------
const handleToggleActive = async (record) => {
  try {
    await toggleUserActive({ user_id: record.id })
    message.success(record.is_active ? '已禁用' : '已启用')
    loadList()
  } catch (e) {
    message.error(e.message || '操作失败')
  }
}
</script>

<template>
  <div class="users-view">
    <a-page-header title="用户管理" sub-title="管理系统用户与角色" style="padding: 0 0 24px 0">
      <template #extra>
        <a-button type="primary" @click="openCreate">
          <template #icon><UserAddOutlined /></template>
          添加用户
        </a-button>
      </template>
    </a-page-header>

    <a-card :bordered="false">
      <div class="filter-toolbar">
        <a-input
          v-model:value="searchText"
          placeholder="搜索工号、真实姓名"
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
        :scroll="{ x: 1200 }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'groups'">
            <a-tag v-for="g in record.groups || []" :key="g.id" style="margin: 0 2px">{{
              g.name
            }}</a-tag>
          </template>
          <template v-else-if="column.key === 'is_active'">
            <a-tag :color="record.is_active ? 'success' : 'error'">
              {{ record.is_active ? '启用' : '禁用' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'is_superuser'">
            <a-tag :color="record.is_superuser ? 'gold' : 'default'">
              {{ record.is_superuser ? '超级管理员' : '普通用户' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="openEdit(record)">编辑</a-button>
              <a-button type="link" size="small" @click="handleResetPassword(record)"
                >重置密码</a-button
              >
              <a-button type="link" size="small" @click="handleToggleActive(record)">
                {{ record.is_active ? '禁用' : '启用' }}
              </a-button>
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
      :title="isEdit ? '编辑用户' : '新建用户'"
      :confirm-loading="modalLoading"
      ok-text="保存"
      @ok="handleModalOk"
    >
      <a-form layout="vertical">
        <a-form-item label="工号" required>
          <a-input v-model:value="formState.username" placeholder="工号" />
        </a-form-item>
        <a-form-item v-if="!isEdit" label="密码">
          <a-input-password v-model:value="formState.password" placeholder="不填则使用默认密码" />
        </a-form-item>
        <a-form-item label="真实姓名">
          <a-input v-model:value="formState.real_name" placeholder="真实姓名" />
        </a-form-item>
        <a-form-item label="角色">
          <a-select
            v-model:value="formState.group_ids"
            mode="multiple"
            placeholder="选择角色"
            style="width: 100%"
            :options="groupOptions.map((g) => ({ label: g.name, value: g.id }))"
          />
        </a-form-item>
        <a-form-item label="启用">
          <a-switch v-model:checked="formState.is_active" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<style scoped>
.users-view {
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
  width: 260px;
}
</style>
