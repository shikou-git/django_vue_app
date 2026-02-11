<template v-for="item in menuItems" :key="item.key">
  <a-sub-menu
    v-if="item.children"
    :key="`sub_${item.key}`"  <!-- 添加唯一前缀 -->
  >
    <template #icon>
      <component :is="item.icon" />
    </template>
    <template #title>{{ item.title }}</template>
    <a-menu-item v-for="child in item.children" :key="child.key">
      {{ child.title }}
    </a-menu-item>
  </a-sub-menu>

  <a-menu-item
    v-else
    :key="`item_${item.key}`"  <!-- 添加不同前缀 -->
  >
    <template #icon>
      <component :is="item.icon" />
    </template>
    {{ item.title }}
  </a-menu-item>
</template>



<script setup>
import {
  DashboardOutlined,
  FileTextOutlined,
  HomeOutlined,
  InfoCircleOutlined,
  SettingOutlined,
  UserOutlined,
} from '@ant-design/icons-vue'
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const selectedKeys = ref([route.path])
const openKeys = ref([])

// 菜单配置
const menuItems = ref([
  {
    key: '/',
    title: '首页',
    icon: HomeOutlined,
  },
  {
    key: '/dashboard',
    title: '仪表盘',
    icon: DashboardOutlined,
    children: [
      { key: '/dashboard/analysis', title: '分析页' },
      { key: '/dashboard/monitor', title: '监控页' },
      { key: '/dashboard/workplace', title: '工作台' },
    ],
  },
  {
    key: '/authorization',
    title: '认证管理',
    icon: UserOutlined,
    children: [
      { key: '/authorization/users', title: '用户管理' },
      { key: '/authorization/roles', title: '角色管理' },
      { key: '/authorization/permissions', title: '权限管理' },
    ],
  },
  {
    key: '/content',
    title: '内容管理',
    icon: FileTextOutlined,
    children: [
      { key: '/content/articles', title: '文章管理' },
      { key: '/content/categories', title: '分类管理' },
      { key: '/content/tags', title: '标签管理' },
    ],
  },
  {
    key: '/settings',
    title: '系统设置',
    icon: SettingOutlined,
    children: [
      { key: '/settings/general', title: '基本设置' },
      { key: '/settings/security', title: '安全设置' },
      { key: '/settings/notification', title: '通知设置' },
    ],
  },
  {
    key: '/about',
    title: '关于',
    icon: InfoCircleOutlined,
  },
])

// 初始化展开的菜单
const initOpenKeys = () => {
  const path = route.path
  menuItems.value.forEach((item) => {
    if (item.children) {
      const hasActive = item.children.some((child) => path.startsWith(child.key))
      if (hasActive && !openKeys.value.includes(item.key)) {
        openKeys.value.push(item.key)
      }
    }
  })
}

initOpenKeys()

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
