<template>
  <a-layout class="admin-layout">
    <a-layout-header class="layout-header">
      <AppHeader @toggle-sidebar="toggleSidebar" :collapsed="collapsed" />
    </a-layout-header>
    <a-layout>
      <a-layout-sider
        v-model:collapsed="collapsed"
        :trigger="null"
        collapsible
        :width="250"
        class="layout-sider"
      >
        <AppSidebar />
      </a-layout-sider>
      <a-layout-content class="layout-content">
        <div class="content-wrapper">
          <router-view />
        </div>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'

const collapsed = ref(false)

const toggleSidebar = () => {
  collapsed.value = !collapsed.value
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
}

.layout-header {
  background: #fff;
  padding: 0;
  height: 64px;
  line-height: 64px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  position: sticky;
  top: 0;
  z-index: 10;
}

.layout-sider {
  background: #001529;
  overflow: auto;
  height: calc(100vh - 64px);
  position: fixed !important;
  left: 0;
  top: 64px;
  bottom: 0;
}

.layout-content {
  margin-left: 250px;
  background: #f0f2f5;
  min-height: calc(100vh - 64px);
  transition: margin-left 0.2s;
}

:deep(.ant-layout-sider-collapsed) + .layout-content {
  margin-left: 80px;
}

.content-wrapper {
  padding: 24px;
  min-height: 360px;
}

@media (max-width: 768px) {
  .layout-content {
    margin-left: 0;
  }
  
  :deep(.ant-layout-sider-collapsed) + .layout-content {
    margin-left: 0;
  }
}
</style>
