<script setup>
import { computed } from 'vue'
import { useRoute, RouterView } from 'vue-router'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import AdminLayout from './components/layout/AdminLayout.vue'

const route = useRoute()
const showLayout = computed(() => !route.meta.hideLayout)
</script>

<template>
  <a-config-provider :locale="zhCN">
    <AdminLayout v-if="showLayout" />
    <RouterView v-else />
  </a-config-provider>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
    'Noto Color Emoji';
}

#app {
  height: 100vh;
  overflow: hidden;
}
</style>
