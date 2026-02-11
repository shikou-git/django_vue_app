<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import {
  UserAddOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
} from '@ant-design/icons-vue'
import { message, Modal } from 'ant-design-vue'
import {
  getUserList,
  getUserDetail,
  createUser,
  updateUser,
  deleteUser,
  resetPassword,
  toggleUserActive,
  getGroupList,
} from '@/api/auth'

const loading = ref(false)
const searchText = ref('')
const isActiveFilter = ref(undefined)
const groupFilter = ref(undefined)
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })
const dataSource = ref([])
const groupOptions = ref([])

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
  { title: '工号', dataIndex: 'username', key: 'username', width: 120 },
  { title: '真实姓名', dataIndex: 'real_name', key: 'real_name', width: 120, ellipsis: true },
  { title: '角色', dataIndex: 'groups', key: 'groups', width: 150, ellipsis: true },
  { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 90 },
  { title: '注册时间', dataIndex: 'date_joined', key: 'date_joined', width: 170 },
  { title: '最后登录', dataIndex: 'last_login', key: 'last_login', width: 170 },
  { title: '操作', key: 'action', width: 260, fixed: 'right' },
]

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
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      search: searchText.value || undefined,
      is_active: isActiveFilter.value,
      group: groupFilter.value,
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

watch([() => pagination.current, () => pagination.pageSize], () => loadList())

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

const handleSearch = () => loadList()

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
  if (!isEdit.value && !formState.password) {
    message.warning('请输入密码')
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
        password: formState.password,
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

// ---------- 重置密码 ----------
const resetPwdVisible = ref(false)
const resetPwdUserId = ref(null)
const resetPwdPassword = ref('')
const resetPwdLoading = ref(false)

const openResetPassword = (record) => {
  resetPwdUserId.value = record.id
  resetPwdPassword.value = ''
  resetPwdVisible.value = true
}

const handleResetPasswordOk = async () => {
  if (!resetPwdPassword.value || resetPwdPassword.value.length < 6) {
    message.warning('请输入至少 6 位新密码')
    return
  }
  resetPwdLoading.value = true
  try {
    await resetPassword({ user_id: resetPwdUserId.value, new_password: resetPwdPassword.value })
    message.success('密码已重置')
    resetPwdVisible.value = false
  } catch (e) {
    message.error(e.message || '重置失败')
  } finally {
    resetPwdLoading.value = false
  }
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
      <a-space style="margin-bottom: 16px" :size="12">
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索工号、真实姓名"
          enter-button
          style="width: 260px"
          allow-clear
          @search="handleSearch"
        >
          <template #prefix><SearchOutlined /></template>
        </a-input-search>
        <a-select
          v-model:value="isActiveFilter"
          placeholder="状态"
          style="width: 110px"
          allow-clear
          @change="handleSearch"
        >
          <a-select-option :value="true">启用</a-select-option>
          <a-select-option :value="false">禁用</a-select-option>
        </a-select>
        <a-select
          v-model:value="groupFilter"
          placeholder="角色"
          style="width: 140px"
          allow-clear
          @change="handleSearch"
        >
          <a-select-option v-for="g in groupOptions" :key="g.id" :value="g.id">{{ g.name }}</a-select-option>
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
        :scroll="{ x: 1200 }"
        @change="(pag) => { pagination.current = pag.current; pagination.pageSize = pag.pageSize }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'groups'">
            <a-tag v-for="g in (record.groups || [])" :key="g.id" style="margin: 0 2px">{{ g.name }}</a-tag>
          </template>
          <template v-else-if="column.key === 'is_active'">
            <a-tag :color="record.is_active ? 'success' : 'default'">
              {{ record.is_active ? '启用' : '禁用' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="openEdit(record)">编辑</a-button>
              <a-button type="link" size="small" @click="openResetPassword(record)">重置密码</a-button>
              <a-button type="link" size="small" @click="handleToggleActive(record)">
                {{ record.is_active ? '禁用' : '启用' }}
              </a-button>
              <a-button type="link" danger size="small" @click="handleDelete(record)">删除</a-button>
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
        <a-form-item v-if="!isEdit" label="密码" required>
          <a-input-password v-model:value="formState.password" placeholder="密码" />
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

    <a-modal
      v-model:open="resetPwdVisible"
      title="重置密码"
      :confirm-loading="resetPwdLoading"
      ok-text="确定"
      @ok="handleResetPasswordOk"
    >
      <a-form-item label="新密码" required>
        <a-input-password v-model:value="resetPwdPassword" placeholder="至少 6 位" />
      </a-form-item>
    </a-modal>
  </div>
</template>

<style scoped>
.users-view {
  max-width: 1400px;
}
</style>
