<template>
  <div class="app-header">
    <div class="header-left">
      <a-button 
        type="text" 
        class="trigger-btn"
        @click="$emit('toggle-sidebar')"
      >
        <template #icon>
          <MenuFoldOutlined v-if="!collapsed" />
          <MenuUnfoldOutlined v-else />
        </template>
      </a-button>
      <div class="logo">
        <span class="logo-text">后台管理系统</span>
      </div>
    </div>
    
    <div class="header-right">
      <a-space :size="16">
        <a-badge :count="3">
          <a-button type="text" shape="circle">
            <template #icon>
              <BellOutlined style="font-size: 18px" />
            </template>
          </a-button>
        </a-badge>
        
        <a-dropdown>
          <div class="user-info">
            <a-avatar style="background-color: #1890ff">
              <template #icon>
                <UserOutlined />
              </template>
            </a-avatar>
            <span class="username">管理员</span>
            <DownOutlined style="font-size: 12px" />
          </div>
          <template #overlay>
            <a-menu>
              <a-menu-item key="profile">
                <UserOutlined />
                个人资料
              </a-menu-item>
              <a-menu-item key="settings">
                <SettingOutlined />
                系统设置
              </a-menu-item>
              <a-menu-divider />
              <a-menu-item key="logout">
                <LogoutOutlined />
                退出登录
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </a-space>
    </div>
  </div>
</template>

<script setup>
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BellOutlined,
  UserOutlined,
  DownOutlined,
  SettingOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue'

defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle-sidebar'])
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.trigger-btn {
  font-size: 18px;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: #001529;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: rgba(0, 0, 0, 0.025);
}

.username {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.85);
}

@media (max-width: 768px) {
  .logo-text {
    display: none;
  }
  
  .username {
    display: none;
  }
}
</style>
