"""
接口日志中间件：在每次请求完成后写入 ApiLog（path、method、status_code、user、ip、user_agent、created_at）。
支持路径排除列表 APILOG_EXCLUDE_PATHS（前缀匹配则不记录）。
"""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from apps.record.models import ApiLog


def get_client_ip(request):
    """从 request 获取客户端 IP（考虑 X-Forwarded-For 等代理头）。"""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def should_skip_log_path(path):
    """若 path 匹配排除列表（前缀匹配）则返回 True，不记录该请求。"""
    if not path:
        return True
    exclude_paths = getattr(settings, "APILOG_EXCLUDE_PATHS", None) or []
    for prefix in exclude_paths:
        if path.startswith(prefix) or path == prefix.rstrip("/"):
            return True
    return False


class ApiLogMiddleware(MiddlewareMixin):
    """在 process_response 中写入一条 ApiLog，避免在 process_request 时尚未得到 status_code。"""

    def process_response(self, request, response):
        try:
            path = (request.path or "").strip()
            if should_skip_log_path(path):
                return response
            user = getattr(request, "user", None)
            user_id = user.pk if (user and user.is_authenticated) else None
            ip = get_client_ip(request)
            user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:512]
            ApiLog.objects.create(
                path=path[:512],
                method=(request.method or "")[:16],
                status_code=response.status_code if response else None,
                user_id=user_id,
                ip_address=ip,
                user_agent=user_agent,
            )
        except Exception:
            pass
        return response
