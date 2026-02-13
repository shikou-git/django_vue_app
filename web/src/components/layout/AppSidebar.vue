<template>
  <div class="app-sidebar-wrap">
    <a-menu
      v-model:selectedKeys="selectedKeys"
      v-model:openKeys="openKeys"
      mode="inline"
      theme="dark"
      class="app-sidebar"
      @click="handleMenuClick"
    >
      <template v-for="item in menuItems" :key="item?.key">
        <a-sub-menu v-if="item?.children?.length" :key="`sub_${item.key}`">
          <template #icon>
            <component :is="item.icon" />
          </template>
          <template #title>{{ item.title }}</template>
          <a-menu-item v-for="child in item.children" :key="child.key">
            {{ child.title }}
          </a-menu-item>
        </a-sub-menu>

        <a-menu-item v-else :key="item.key">
          <template #icon>
            <component :is="item.icon" />
          </template>
          {{ item.title }}
        </a-menu-item>
      </template>
    </a-menu>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { SIDEBAR_DEFAULT_EXPAND_ALL } from '@/utils/const'
import { AuditOutlined, HomeOutlined, UserOutlined } from '@ant-design/icons-vue'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const selectedKeys = ref([route.path])
const openKeys = ref([])

// 菜单配置（原始数据）
const menuItemsRaw = ref([
  {
    key: '/',
    title: '首页',
    icon: HomeOutlined,
  },
  {
    key: '/authorization',
    title: '认证管理',
    icon: UserOutlined,
    children: [
      { key: '/authorization/users', title: '用户管理', permission: 'auth.view_user' },
      { key: '/authorization/roles', title: '角色管理', permission: 'auth.view_group' },
      { key: '/authorization/permissions', title: '权限管理', permission: 'auth.view_permission' },
    ],
  },
  {
    key: '/logs',
    title: '日志管理',
    icon: AuditOutlined,
    children: [
      { key: '/apilog', title: '接口日志', permission: 'apilog.view_apilog' },
      { key: '/api_stats', title: '接口统计', permission: 'apilog.view_apilog' },
    ],
  },
])

if (SIDEBAR_DEFAULT_EXPAND_ALL) {
  openKeys.value = menuItemsRaw.value
    .filter((i) => i.children?.length)
    .map((i) => `sub_${i.key}`)
}

// 根据权限过滤菜单：无 view_user / view_group / view_permission 则不显示对应用户管理、角色管理、权限管理
const menuItems = computed(() => {
  const user = authStore.user
  const isSuper = user?.is_superuser === true
  const perms = user?.permissions || []

  const hasPerm = (perm) => isSuper || perms.includes(perm)

  return menuItemsRaw.value
    .map((item) => {
      if (!item.children?.length) return item
      const children = item.children.filter(
        (child) => !child.permission || hasPerm(child.permission),
      )
      if (children.length === 0) return null
      return { ...item, children }
    })
    .filter(Boolean)
})

// 初始化展开的菜单（仅当未配置“默认全部展开”时，展开当前所在菜单）
const initOpenKeys = () => {
  const path = route.path
  const subKey = (key) => `sub_${key}`
  menuItemsRaw.value.forEach((item) => {
    if (item.children) {
      const hasActive = item.children.some((child) => path.startsWith(child.key))
      if (hasActive && !openKeys.value.includes(subKey(item.key))) {
        openKeys.value.push(subKey(item.key))
      }
    }
  })
}

if (!SIDEBAR_DEFAULT_EXPAND_ALL) {
  initOpenKeys()
}

// 监听路由变化更新选中的菜单
watch(
  () => route.path,
  (newPath) => {
    selectedKeys.value = [newPath]
    initOpenKeys()
  },
)

// 菜单点击处理
const handleMenuClick = ({ key }) => {
  router.push(key)
}
</script>

<style scoped>
.app-sidebar-wrap {
  height: 100%;
}

.app-sidebar {
  height: 100%;
}

:deep(.ant-menu-dark) {
  background: #001529;
}

:deep(.ant-menu-inline) {
  border-right: none;
}
</style>
