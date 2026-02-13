<template>
  <div class="base-settings-view">
    <a-page-header title="基本设置" sub-title="" style="padding: 0 0 24px 0" />

    <a-card :bordered="false">
      <a-form
        :model="form"
        layout="vertical"
        :wrapper-col="{ span: 10 }"
        @finish="onSave"
      >
        <a-form-item name="announcement_content">
          <template #label><span class="form-label-bold">公告内容</span></template>
          <a-textarea
            v-model:value="form.announcement_content"
            placeholder="请输入公告内容"
            :rows="3"
            :maxlength="80"
            show-count
            class="textarea-no-resize"
          />
        </a-form-item>
        <a-form-item name="announcement_enabled">
          <template #label><span class="form-label-bold">启用公告</span></template>
          <a-switch v-model:checked="form.announcement_enabled" />
          <span class="switch-tip">开启后，公告内容将显示在顶部栏</span>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="saving">
            保存
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { getBaseSettings, updateBaseSettings } from '@/api/system'
import { message } from 'ant-design-vue'
import { onMounted, reactive, ref } from 'vue'

const saving = ref(false)
const form = reactive({
  announcement_content: '',
  announcement_enabled: false,
})

async function load() {
  try {
    const res = await getBaseSettings()
    const d = res.data || {}
    form.announcement_content = d.announcement_content ?? ''
    form.announcement_enabled = !!d.announcement_enabled
  } catch (e) {
    message.error(e.message || '加载失败')
  }
}

async function onSave() {
  saving.value = true
  try {
    await updateBaseSettings({
      announcement_content: form.announcement_content,
      announcement_enabled: form.announcement_enabled,
    })
    message.success('保存成功')
    window.dispatchEvent(new CustomEvent('base-settings-updated'))
  } catch (e) {
    message.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.base-settings-view {
  width: 100%;
}
.form-label-bold {
  font-weight: 600;
}
.textarea-no-resize :deep(textarea) {
  resize: none;
}
.switch-tip {
  margin-left: 8px;
  color: rgba(0, 0, 0, 0.45);
  font-size: 13px;
}
</style>
