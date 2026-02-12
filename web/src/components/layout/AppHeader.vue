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
              {{ (auth.user && auth.user.username && auth.user.username[0]) || '?' }}
            </a-avatar>
            <span class="username">{{ (auth.user && auth.user.username) || '用户' }}</span>
            <DownOutlined style="font-size: 12px" />
          </div>
          <template #overlay>
            <a-menu @click="handleMenuClick">
              <a-menu-item key="center">
                <UserOutlined />
                个人中心
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

    <a-drawer
      v-model:open="centerVisible"
      title="个人中心"
      placement="right"
      width="400"
    >
      <div class="center-content">
        <a-tabs v-model:activeKey="centerTabKey">
          <a-tab-pane key="password" tab="修改密码">
            <a-form
              ref="pwdFormRef"
              :model="pwdForm"
              :rules="pwdRules"
              layout="vertical"
              @finish="onChangePassword"
            >
              <a-form-item label="原密码" name="old_password">
                <a-input-password v-model:value="pwdForm.old_password" placeholder="请输入原密码" />
              </a-form-item>
              <a-form-item label="新密码" name="new_password">
                <a-input-password v-model:value="pwdForm.new_password" placeholder="请输入新密码" />
              </a-form-item>
              <a-form-item label="确认新密码" name="confirm_password">
                <a-input-password v-model:value="pwdForm.confirm_password" placeholder="请再次输入新密码" />
              </a-form-item>
              <a-form-item>
                <a-button type="primary" html-type="submit" :loading="pwdLoading">
                  确认修改
                </a-button>
              </a-form-item>
            </a-form>
          </a-tab-pane>
          <a-tab-pane key="avatar" tab="修改头像">
            <div class="tab-placeholder">修改头像功能待实现</div>
          </a-tab-pane>
        </a-tabs>
      </div>
    </a-drawer>
  </div>
</template>

<script setup>
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BellOutlined,
  UserOutlined,
  DownOutlined,
  LogoutOutlined,
} from '@ant-design/icons-vue'
import { ref, reactive } from 'vue'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'
import { changePassword as apiChangePassword } from '@/api/auth'

defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['toggle-sidebar'])

const auth = useAuthStore()
const centerVisible = ref(false)
const centerTabKey = ref('password')
const pwdFormRef = ref(null)
const pwdLoading = ref(false)
const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})
const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码' }],
  new_password: [{ required: true, message: '请输入新密码' }],
  confirm_password: [
    { required: true, message: '请再次输入新密码' },
    {
      validator: (_, value) =>
        value && value === pwdForm.new_password
          ? Promise.resolve()
          : Promise.reject(new Error('两次输入的新密码不一致')),
    },
  ],
}

const handleMenuClick = ({ key }) => {
  if (key === 'center') {
    centerVisible.value = true
  } else if (key === 'logout') {
    auth.logout()
  }
}

async function onChangePassword() {
  pwdLoading.value = true
  try {
    await apiChangePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password,
      confirm_password: pwdForm.confirm_password,
    })
    message.success('密码修改成功，请重新登录')
    centerVisible.value = false
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm_password = ''
    pwdFormRef.value?.resetFields()
    auth.logout()
  } catch (e) {
    message.error(e.message || '修改失败')
  } finally {
    pwdLoading.value = false
  }
}
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

.center-content {
  padding: 0 8px;
}

.tab-placeholder {
  color: rgba(0, 0, 0, 0.45);
  font-size: 14px;
  padding: 24px 0;
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
