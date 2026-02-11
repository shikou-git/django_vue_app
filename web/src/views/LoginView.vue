<script setup>
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const loading = ref(false)

const formState = reactive({
  username: '',
  password: '',
  remember: true,
})

const handleLogin = async () => {
  if (!formState.username || !formState.password) {
    message.warning('请输入工号和密码')
    return
  }
  loading.value = true
  try {
    await auth.login({ username: formState.username.trim(), password: formState.password })
    message.success('登录成功')
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    message.error(e.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="login-title">后台管理系统</h1>
        <p class="login-subtitle">欢迎登录</p>
      </div>

      <a-form
        :model="formState"
        @finish="handleLogin"
        layout="vertical"
        size="large"
      >
        <a-form-item
          name="username"
          :rules="[{ required: true, message: '请输入工号' }]"
        >
          <a-input 
            v-model:value="formState.username" 
            placeholder="用户名"
          >
            <template #prefix>
              <UserOutlined style="color: rgba(0, 0, 0, 0.25)" />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item
          name="password"
          :rules="[{ required: true, message: '请输入密码' }]"
        >
          <a-input-password 
            v-model:value="formState.password" 
            placeholder="密码"
          >
            <template #prefix>
              <LockOutlined style="color: rgba(0, 0, 0, 0.25)" />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item>
          <div style="display: flex; justify-content: space-between; align-items: center">
            <a-checkbox v-model:checked="formState.remember">
              记住我
            </a-checkbox>
            <a href="#" style="color: #1890ff">忘记密码？</a>
          </div>
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            block
            size="large"
            :loading="loading"
            style="height: 48px; font-size: 16px"
          >
            登录
          </a-button>
        </a-form-item>

        <div style="text-align: center">
          <span style="color: rgba(0, 0, 0, 0.45)">还没有账号？</span>
          <a href="#" style="color: #1890ff; margin-left: 4px">立即注册</a>
        </div>
      </a-form>
    </div>

    <div class="login-bg">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  padding: 48px 40px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  z-index: 10;
  animation: slideUp 0.5s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 14px;
  color: #909399;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  bottom: -50px;
  right: -50px;
  animation-delay: 2s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  right: 10%;
  animation-delay: 4s;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
  }
}

@media (max-width: 768px) {
  .login-card {
    margin: 20px;
    padding: 32px 24px;
  }

  .login-title {
    font-size: 24px;
  }
}
</style>
