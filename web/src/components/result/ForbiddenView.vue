<template>
  <div class="forbidden-wrap">
    <a-result
      status="403"
      title="403"
      sub-title="抱歉，您没有权限访问该页面。"
    >
      <template #extra>
        <a-button type="primary" @click="goHome">返回首页</a-button>
      </template>
    </a-result>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const goHome = () => router.push('/')
</script>

<style scoped>
.forbidden-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 24px;
}
</style>
