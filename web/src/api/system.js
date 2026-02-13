/**
 * system.js
 * 系统设置相关 API（基本设置等）
 */
import request from './request'

/** 获取基本设置（公告内容、公告开关），任意登录用户可读 */
export function getBaseSettings(data = {}) {
  return request.post('/system/get_base_settings/', data)
}

/** 更新基本设置，需要权限 system.change_basesetting */
export function updateBaseSettings(data) {
  return request.post('/system/update_base_settings/', data)
}
