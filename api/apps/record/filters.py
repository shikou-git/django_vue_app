import django_filters
from django.db.models import Q

from apps.record.models import ApiLog


class ApiLogFilter(django_filters.FilterSet):
    """接口日志过滤器"""

    ORDER_MAP = {
        "path": "path",
        "method": "method",
        "status_code": "status_code",
        "user_id": "user_id",
        "ip_address": "ip_address",
        "created_at": "created_at",
    }

    search = django_filters.CharFilter(method="filter_search", label="综合搜索（path、user_agent）")
    path = django_filters.Filter(method="filter_paths", label="路径（多选）")
    method = django_filters.CharFilter(field_name="method", label="请求方法")
    status_code = django_filters.Filter(method="filter_status_codes", label="状态码（多选）")
    user_id = django_filters.Filter(method="filter_user_ids", label="用户ID（多选）")
    ip_address = django_filters.Filter(method="filter_ip_addresses", label="IP（多选）")
    created_at_start = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte", label="开始时间")
    created_at_end = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte", label="结束时间")

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(Q(path__icontains=value) | Q(user_agent__icontains=value))
        return queryset

    def filter_paths(self, queryset, name, value):
        """路径多选筛选"""
        if not value or not isinstance(value, list):
            return queryset
        return queryset.filter(path__in=value)

    def filter_status_codes(self, queryset, name, value):
        """状态码多选筛选"""
        if not value or not isinstance(value, list):
            return queryset
        return queryset.filter(status_code__in=value)

    def filter_user_ids(self, queryset, name, value):
        """用户ID多选筛选；value 中可含 __null__ 表示筛选 user_id 为空的记录（未登录）"""
        if not value or not isinstance(value, list):
            return queryset
        has_null = "__null__" in value
        ids = [v for v in value if v != "__null__"]
        if has_null and ids:
            return queryset.filter(Q(user_id__isnull=True) | Q(user_id__in=ids))
        if has_null:
            return queryset.filter(user_id__isnull=True)
        return queryset.filter(user_id__in=ids)

    def filter_ip_addresses(self, queryset, name, value):
        """IP多选筛选"""
        if not value or not isinstance(value, list):
            return queryset
        return queryset.filter(ip_address__in=value)

    class Meta:
        model = ApiLog
        fields = ["search", "path", "method", "status_code", "user_id", "ip_address", "created_at_start", "created_at_end"]
