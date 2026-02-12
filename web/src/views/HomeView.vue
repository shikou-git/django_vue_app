<script setup>
import { ref } from 'vue'
import {
  UserOutlined,
  EyeOutlined,
  ShoppingOutlined,
  DollarOutlined,
  FileAddOutlined,
  UserAddOutlined,
  FolderAddOutlined,
  SettingOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined
} from '@ant-design/icons-vue'

const stats = ref([
  { 
    title: '总用户数', 
    value: '12,345', 
    icon: UserOutlined, 
    color: '#1890ff', 
    change: 12,
    prefix: ''
  },
  { 
    title: '今日访问', 
    value: '3,456', 
    icon: EyeOutlined, 
    color: '#52c41a', 
    change: 5,
    prefix: ''
  },
  { 
    title: '总订单数', 
    value: '8,234', 
    icon: ShoppingOutlined, 
    color: '#faad14', 
    change: 18,
    prefix: ''
  },
  { 
    title: '总收入', 
    value: '234,567', 
    icon: DollarOutlined, 
    color: '#f5222d', 
    change: 23,
    prefix: '¥'
  }
])

const recentActivities = ref([
  { user: '张三', action: '创建了新文章', time: '5分钟前' },
  { user: '李四', action: '修改了用户权限', time: '15分钟前' },
  { user: '王五', action: '上传了新图片', time: '1小时前' },
  { user: '赵六', action: '删除了过期数据', time: '2小时前' }
])

const quickActions = ref([
  { title: '新建文章', icon: FileAddOutlined },
  { title: '添加用户', icon: UserAddOutlined },
  { title: '上传文件', icon: FolderAddOutlined },
  { title: '系统设置', icon: SettingOutlined }
])
</script>

<template>
  <div class="home-view">
    <a-page-header
      title="欢迎回来！"
      sub-title="这是你的后台管理系统首页"
      style="padding: 0 0 24px 0"
    />

    <a-row :gutter="[16, 16]" style="margin-bottom: 24px">
      <a-col :xs="24" :sm="12" :lg="6" v-for="stat in stats" :key="stat.title">
        <a-card hoverable>
          <a-statistic
            :title="stat.title"
            :value="stat.value"
            :prefix="stat.prefix"
            :value-style="{ color: stat.color }"
          >
            <template #prefix>
              <component :is="stat.icon" :style="{ color: stat.color, marginRight: '8px' }" />
            </template>
            <template #suffix>
              <a-tag :color="stat.change > 0 ? 'success' : 'error'" style="margin-left: 8px">
                <component :is="stat.change > 0 ? ArrowUpOutlined : ArrowDownOutlined" />
                {{ Math.abs(stat.change) }}%
              </a-tag>
            </template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :lg="12">
        <a-card title="最近活动" :bordered="false">
          <a-list item-layout="horizontal" :data-source="recentActivities">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta :description="item.time">
                  <template #title>
                    <strong>{{ item.user }}</strong> {{ item.action }}
                  </template>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: '#1890ff' }">
                      {{ item.user.charAt(0) }}
                    </a-avatar>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>

      <a-col :xs="24" :lg="12">
        <a-card title="快捷操作" :bordered="false">
          <a-row :gutter="[12, 12]">
            <a-col :span="12" v-for="action in quickActions" :key="action.title">
              <a-button type="dashed" block size="large" style="height: 64px">
                <component :is="action.icon" style="font-size: 20px" />
                <div>{{ action.title }}</div>
              </a-button>
            </a-col>
          </a-row>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<style scoped>
.home-view {
  width: 100%;
}

:deep(.ant-statistic-title) {
  margin-bottom: 8px;
}

:deep(.ant-btn) {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
</style>
