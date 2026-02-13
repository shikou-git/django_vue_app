// apilog.js
import request, { downloadFile } from './request'

/** 接口日志列表（分页、筛选、排序） */
export function getApilogList(data) {
  return request.post('/apilog/get_apilog_list/', data)
}

/** 删除单条接口日志 */
export function deleteApilog(data) {
  return request.post('/apilog/delete_apilog/', data)
}

/** 批量删除接口日志 */
export function batchDeleteApilog(data) {
  return request.post('/apilog/batch_delete_apilog/', data)
}

/** 获取筛选字段的选项（多选用） */
export function getFilterOptions(data) {
  return request.post('/apilog/get_filter_options/', data)
}

/** 接口统计：接口调用量排行、Top 用户调用量排行。body: filter_type, year, month, day, date_start, date_end */
export function getApiStats(data) {
  return request.post('/apilog/get_api_stats/', data)
}

/** 导出接口日志为 CSV */
export function exportApilog(data = {}) {
  return downloadFile('/apilog/export_apilog/', data)
}
