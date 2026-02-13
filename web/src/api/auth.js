/**
 * auth.js
 * 认证与用户、权限管理相关 API（与后端 POST 接口一一对应）
 */
import request from './request'

// ---------- 登录与登出 ----------
export function login(data) {
  return request.post('/auth/login/', data)
}

export function logout(data = {}) {
  return request.post('/auth/logout/', data)
}

export function refreshToken(data) {
  return request.post('/auth/refresh_token/', data)
}

export function getCurrentUser() {
  return request.post('/auth/get_current_user/')
}

// ---------- 用户管理 ----------
export function getUserList(data) {
  return request.post('/auth/get_user_list/', data)
}

export function getUserDetail(data) {
  return request.post('/auth/get_user_detail/', data)
}

export function createUser(data) {
  return request.post('/auth/create_user/', data)
}

export function updateUser(data) {
  return request.post('/auth/update_user/', data)
}

export function deleteUser(data) {
  return request.post('/auth/delete_user/', data)
}

export function resetPassword(data) {
  return request.post('/auth/reset_password/', data)
}

/** 当前用户修改自己的密码 */
export function changePassword(data) {
  return request.post('/auth/change_password/', data)
}

export function toggleUserActive(data) {
  return request.post('/auth/toggle_user_active/', data)
}

// ---------- 角色管理 ----------
export function getGroupList(data = {}) {
  return request.post('/auth/get_group_list/', data)
}

export function getGroupDetail(data) {
  return request.post('/auth/get_group_detail/', data)
}

export function createGroup(data) {
  return request.post('/auth/create_group/', data)
}

export function updateGroup(data) {
  return request.post('/auth/update_group/', data)
}

export function deleteGroup(data) {
  return request.post('/auth/delete_group/', data)
}

// ---------- 用户角色管理（单独加入/移出角色） ----------
export function addUserToGroup(data) {
  return request.post('/auth/add_user_to_group/', data)
}

export function removeUserFromGroup(data) {
  return request.post('/auth/remove_user_from_group/', data)
}

// ---------- 权限管理 ----------
export function getPermissionList(data) {
  return request.post('/auth/get_permission_list/', data)
}

export function getPermissionDetail(data) {
  return request.post('/auth/get_permission_detail/', data)
}

export function getPermissionFilterOptions(data = {}) {
  return request.post('/auth/get_permission_filter_options/', data)
}
