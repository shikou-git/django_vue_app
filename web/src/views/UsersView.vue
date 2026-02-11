<script setup>
import { ref } from 'vue'
import { 
  UserAddOutlined, 
  EditOutlined, 
  DeleteOutlined,
  SearchOutlined 
} from '@ant-design/icons-vue'

const searchText = ref('')
const selectedRowKeys = ref([])

const columns = [
  {
    title: '用户名',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email',
  },
  {
    title: '角色',
    dataIndex: 'role',
    key: 'role',
    filters: [
      { text: '管理员', value: 'admin' },
      { text: '编辑', value: 'editor' },
      { text: '用户', value: 'user' },
    ],
    onFilter: (value, record) => record.role === value,
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    filters: [
      { text: '活跃', value: 'active' },
      { text: '未激活', value: 'inactive' },
      { text: '已禁用', value: 'banned' },
    ],
    onFilter: (value, record) => record.status === value,
  },
  {
    title: '注册时间',
    dataIndex: 'createdAt',
    key: 'createdAt',
    sorter: (a, b) => new Date(a.createdAt) - new Date(b.createdAt),
  },
  {
    title: '操作',
    key: 'action',
  },
]

const dataSource = ref([
  { 
    key: '1', 
    name: '张三', 
    email: 'zhangsan@example.com', 
    role: 'admin', 
    status: 'active', 
    createdAt: '2026-01-15' 
  },
  { 
    key: '2', 
    name: '李四', 
    email: 'lisi@example.com', 
    role: 'editor', 
    status: 'active', 
    createdAt: '2026-01-20' 
  },
  { 
    key: '3', 
    name: '王五', 
    email: 'wangwu@example.com', 
    role: 'user', 
    status: 'active', 
    createdAt: '2026-01-25' 
  },
  { 
    key: '4', 
    name: '赵六', 
    email: 'zhaoliu@example.com', 
    role: 'user', 
    status: 'inactive', 
    createdAt: '2026-02-01' 
  },
  { 
    key: '5', 
    name: '钱七', 
    email: 'qianqi@example.com', 
    role: 'editor', 
    status: 'active', 
    createdAt: '2026-02-05' 
  },
  { 
    key: '6', 
    name: '孙八', 
    email: 'sunba@example.com', 
    role: 'user', 
    status: 'banned', 
    createdAt: '2026-02-08' 
  },
])

const getRoleTag = (role) => {
  const tagMap = {
    admin: { color: 'red', text: '管理员' },
    editor: { color: 'blue', text: '编辑' },
    user: { color: 'default', text: '用户' }
  }
  return tagMap[role] || tagMap.user
}

const getStatusTag = (status) => {
  const tagMap = {
    active: { color: 'success', text: '活跃' },
    inactive: { color: 'warning', text: '未激活' },
    banned: { color: 'error', text: '已禁用' }
  }
  return tagMap[status] || tagMap.inactive
}

const onSelectChange = (keys) => {
  selectedRowKeys.value = keys
}

const handleEdit = (record) => {
  console.log('编辑用户:', record)
}

const handleDelete = (record) => {
  console.log('删除用户:', record)
}
</script>

<template>
  <div class="users-view">
    <a-page-header
      title="用户管理"
      sub-title="管理系统用户信息和权限"
      style="padding: 0 0 24px 0"
    >
      <template #extra>
        <a-button type="primary" size="large">
          <template #icon>
            <UserAddOutlined />
          </template>
          添加用户
        </a-button>
      </template>
    </a-page-header>

    <a-card :bordered="false">
      <a-space style="margin-bottom: 16px" :size="12">
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索用户名、邮箱..."
          enter-button
          style="width: 300px"
          allow-clear
        >
          <template #prefix>
            <SearchOutlined />
          </template>
        </a-input-search>
        
        <a-select
          placeholder="全部角色"
          style="width: 120px"
          allow-clear
        >
          <a-select-option value="admin">管理员</a-select-option>
          <a-select-option value="editor">编辑</a-select-option>
          <a-select-option value="user">用户</a-select-option>
        </a-select>
        
        <a-select
          placeholder="全部状态"
          style="width: 120px"
          allow-clear
        >
          <a-select-option value="active">活跃</a-select-option>
          <a-select-option value="inactive">未激活</a-select-option>
          <a-select-option value="banned">已禁用</a-select-option>
        </a-select>
      </a-space>

      <a-table
        :columns="columns"
        :data-source="dataSource"
        :row-selection="{
          selectedRowKeys: selectedRowKeys,
          onChange: onSelectChange,
        }"
        :pagination="{
          total: dataSource.length,
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`
        }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <a-space>
              <a-avatar :style="{ backgroundColor: '#1890ff' }">
                {{ record.name.charAt(0) }}
              </a-avatar>
              <span>{{ record.name }}</span>
            </a-space>
          </template>
          
          <template v-if="column.key === 'role'">
            <a-tag :color="getRoleTag(record.role).color">
              {{ getRoleTag(record.role).text }}
            </a-tag>
          </template>
          
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusTag(record.status).color">
              {{ getStatusTag(record.status).text }}
            </a-tag>
          </template>
          
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleEdit(record)">
                <template #icon>
                  <EditOutlined />
                </template>
              </a-button>
              <a-button type="link" danger size="small" @click="handleDelete(record)">
                <template #icon>
                  <DeleteOutlined />
                </template>
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<style scoped>
.users-view {
  max-width: 1400px;
}
</style>
