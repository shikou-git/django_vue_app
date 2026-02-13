import csv
from io import StringIO

from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view

from apps.apilog.filters import ApiLogFilter
from apps.apilog.models import ApiLog
from utils.custom_decorators import check_permission
from utils.custom_response import Resp


def _log_to_dict(log):
    """单条日志转字典，时间转为本地格式"""
    created_at_str = ""
    if log.created_at:
        local_dt = timezone.localtime(log.created_at)
        created_at_str = local_dt.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "id": log.id,
        "path": log.path or "",
        "method": log.method or "",
        "status_code": log.status_code,
        "user_id": log.user_id,
        "ip_address": log.ip_address or "",
        "user_agent": (log.user_agent or "")[:200],
        "created_at": created_at_str,
    }


@api_view(["POST"])
@check_permission("apilog.view_apilog")
def get_apilog_list(request):
    """
    接口日志列表：分页、筛选、排序。
    POST body: page, page_size, search, path, method, status_code, user_id, ip_address,
               created_at_start, created_at_end, order_by (e.g. ["-created_at"])
    """
    data = request.data or {}
    filter_params = {k: data[k] for k in ApiLogFilter.base_filters if k in data}
    queryset = ApiLogFilter(data=filter_params, queryset=ApiLog.objects.all()).qs

    order_by = data.get("order_by")
    if order_by and isinstance(order_by, list) and len(order_by) > 0:
        order_fields = []
        for key in order_by:
            if not isinstance(key, str):
                continue
            desc = key.startswith("-")
            raw = key[1:] if desc else key
            if raw in ApiLogFilter.ORDER_MAP:
                orm_field = ApiLogFilter.ORDER_MAP[raw]
                order_fields.append("-" + orm_field if desc else orm_field)
        if order_fields:
            queryset = queryset.order_by(*order_fields)
        else:
            queryset = queryset.order_by("created_at")
    else:
        queryset = queryset.order_by("created_at")

    page = data.get("page", 1)
    page_size = data.get("page_size", 10)
    page = max(1, int(page) if page is not None else 1)
    page_size = max(1, min(int(page_size) if page_size is not None else 10, 100))
    start = (page - 1) * page_size
    end = start + page_size

    total = queryset.count()
    logs = queryset[start:end]
    results = [_log_to_dict(log) for log in logs]

    return Resp.success(
        data={"results": results, "total": total, "page": page, "page_size": page_size},
        msg="获取成功",
    )


@api_view(["POST"])
@check_permission("apilog.export_apilog")
def export_apilog(request):
    """
    导出接口日志为 CSV。使用与列表相同的筛选参数，不分页，最多导出 10000 条。
    """
    data = request.data or {}
    filter_params = {k: data[k] for k in ApiLogFilter.base_filters if k in data}
    queryset = ApiLogFilter(data=filter_params, queryset=ApiLog.objects.all()).qs
    queryset = queryset.order_by("-created_at")[:10000]

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "path", "method", "status_code", "user_id", "ip_address", "user_agent", "created_at"])
    for log in queryset:
        created_at_str = ""
        if log.created_at:
            local_dt = timezone.localtime(log.created_at)
            created_at_str = local_dt.strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([
            log.id,
            log.path or "",
            log.method or "",
            log.status_code or "",
            log.user_id or "",
            log.ip_address or "",
            (log.user_agent or "")[:512],
            created_at_str,
        ])

    response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8-sig")
    filename = f"api_log_{timezone.localtime(timezone.now()).strftime('%Y%m%d_%H%M%S')}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@api_view(["POST"])
@check_permission("apilog.delete_apilog")
def delete_apilog(request):
    """删除单条接口日志。POST body: id"""
    log_id = request.data.get("id")
    if not log_id:
        return Resp.bad_request(msg="id 是必填项")
    try:
        log = ApiLog.objects.get(id=log_id)
        log.delete()
        return Resp.success(msg="删除成功")
    except ApiLog.DoesNotExist:
        return Resp.not_found(msg="日志不存在")


@api_view(["POST"])
@check_permission("apilog.delete_apilog")
def batch_delete_apilog(request):
    """批量删除接口日志。POST body: ids (列表)"""
    ids = request.data.get("ids")
    if not ids or not isinstance(ids, list):
        return Resp.bad_request(msg="ids 必填且为数组")
    ids = [x for x in ids if isinstance(x, (int, str)) and str(x).isdigit()]
    ids = list(set(int(x) for x in ids))
    if not ids:
        return Resp.bad_request(msg="ids 不能为空")
    deleted, _ = ApiLog.objects.filter(id__in=ids).delete()
    return Resp.success(data={"deleted": deleted}, msg=f"已删除 {deleted} 条")


@api_view(["POST"])
@check_permission("apilog.view_apilog")
def get_filter_options(request):
    """
    获取指定字段的去重选项（用于多选筛选）。
    POST body: field (path/status_code/user_id/ip_address), search (可选，模糊搜索)
    返回最多 100 个选项。
    """
    data = request.data or {}
    field = data.get("field")
    search = (data.get("search") or "").strip()
    
    if field not in ["path", "status_code", "user_id", "ip_address"]:
        return Resp.bad_request(msg="field 必须为 path/status_code/user_id/ip_address")
    
    queryset = ApiLog.objects.all()
    if search:
        queryset = queryset.filter(**{f"{field}__icontains": search})
    
    values = (
        queryset.values_list(field, flat=True)
        .exclude(**{field: None})
        .distinct()
        .order_by(field)[:100]
    )
    
    options = [{"label": str(v), "value": v} for v in values]
    return Resp.success(data={"options": options}, msg="获取成功")
