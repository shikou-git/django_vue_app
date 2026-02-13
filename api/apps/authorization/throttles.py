# throttles.py
"""
登录接口限流：按 IP 限制请求频率，防止暴力破解。
"""
from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """
    登录接口专用限流：未认证用户按 IP 限制。
    速率由 settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login'] 配置，如 '5/min'、'10/hour'。
    """
    scope = "login"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            return None  # 已登录用户调用登录接口时不限流（如刷新页重复提交）
        return self.get_ident(request)
