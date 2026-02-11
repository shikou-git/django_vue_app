# filters.py
import django_filters
from django.contrib.auth.models import User, Permission
from django.db.models import Q


class PermissionFilter(django_filters.FilterSet):
    """权限过滤器"""

    search = django_filters.CharFilter(method="filter_search", label="综合搜索（权限名称、codename）")
    content_type = django_filters.NumberFilter(field_name="content_type_id", label="内容类型ID")

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value) | Q(codename__icontains=value)
            )
        return queryset

    class Meta:
        model = Permission
        fields = ["search", "content_type"]


class UserFilter(django_filters.FilterSet):
    """用户过滤器"""

    # 搜索字段（多字段模糊搜索）
    search = django_filters.CharFilter(method="filter_search", label="综合搜索（用户名、邮箱、姓名、工号）")

    # 状态过滤
    is_active = django_filters.BooleanFilter(field_name="is_active", label="是否激活")

    is_staff = django_filters.BooleanFilter(field_name="is_staff", label="是否员工")

    is_superuser = django_filters.BooleanFilter(field_name="is_superuser", label="是否超级用户")

    # 分组过滤
    group = django_filters.NumberFilter(field_name="groups__id", label="所属分组ID")

    # 工号过滤
    employee_id = django_filters.CharFilter(field_name="profile__employee_id", lookup_expr="icontains", label="工号")

    # 日期范围过滤
    date_joined_start = django_filters.DateFilter(field_name="date_joined", lookup_expr="gte", label="注册开始日期")

    date_joined_end = django_filters.DateFilter(field_name="date_joined", lookup_expr="lte", label="注册结束日期")

    # 最后登录时间过滤
    last_login_start = django_filters.DateFilter(field_name="last_login", lookup_expr="gte", label="最后登录开始时间")

    last_login_end = django_filters.DateFilter(field_name="last_login", lookup_expr="lte", label="最后登录结束时间")

    def filter_search(self, queryset, name, value):
        """综合搜索方法"""
        if value:
            return queryset.filter(
                Q(username__icontains=value)
                | Q(email__icontains=value)
                | Q(first_name__icontains=value)
                | Q(last_name__icontains=value)
                | Q(profile__employee_id__icontains=value)
            )
        return queryset

    class Meta:
        model = User
        fields = [
            "search",
            "is_active",
            "is_staff",
            "is_superuser",
            "group",
            "employee_id",
            "date_joined_start",
            "date_joined_end",
            "last_login_start",
            "last_login_end",
        ]
