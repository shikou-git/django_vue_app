<script setup>
import { ref } from 'vue'
import { CheckCircleOutlined } from '@ant-design/icons-vue'

const systemInfo = ref([
  { label: '系统名称', value: '后台管理系统' },
  { label: '版本号', value: 'v1.0.0' },
  { label: '前端框架', value: 'Vue 3 + Vite + Ant Design Vue' },
  { label: '后端框架', value: 'Django' },
  { label: '开发者', value: '您的团队' },
  { label: '发布日期', value: '2026-02-11' },
])

const techStack = [
  'Vue 3',
  'Vite',
  'Vue Router',
  'Pinia',
  'Ant Design Vue',
  'Django',
  'Python'
]

const features = [
  '响应式布局设计',
  '侧边栏菜单导航',
  '顶部导航栏',
  '用户权限管理',
  '内容管理系统',
  '系统设置功能'
]
</script>

<template>
  <div class="about-view">
    <a-page-header
      title="关于系统"
      sub-title="系统信息和技术栈"
      style="padding: 0 0 24px 0"
    />

    <a-card title="系统信息" :bordered="false" style="margin-bottom: 16px">
      <a-descriptions :column="{ xs: 1, sm: 2, md: 2, lg: 2 }" bordered>
        <a-descriptions-item 
          v-for="item in systemInfo" 
          :key="item.label"
          :label="item.label"
        >
          {{ item.value }}
        </a-descriptions-item>
      </a-descriptions>
    </a-card>

    <a-row :gutter="16">
      <a-col :xs="24" :lg="12">
        <a-card title="技术栈" :bordered="false" style="margin-bottom: 16px">
          <a-space wrap :size="8">
            <a-tag 
              v-for="tech in techStack" 
              :key="tech"
              color="blue"
              style="padding: 4px 12px; font-size: 14px"
            >
              {{ tech }}
            </a-tag>
          </a-space>
        </a-card>
      </a-col>

      <a-col :xs="24" :lg="12">
        <a-card title="功能特性" :bordered="false">
          <a-list :data-source="features" :split="false">
            <template #renderItem="{ item }">
              <a-list-item style="padding: 8px 0">
                <CheckCircleOutlined style="color: #52c41a; margin-right: 8px" />
                {{ item }}
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<style scoped>
.about-view {
  width: 100%;
}
</style>
