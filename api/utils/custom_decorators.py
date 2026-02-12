# utils/decorators.py - 权限白名单与鉴权装饰器
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, BasePermission


def skip_permission(func):
    return permission_classes([AllowAny])(func)


def skip_authentication(func):
    return authentication_classes([])(func)


def check_permission(full_perm: str):
    """
    接口鉴权装饰器：要求当前用户拥有指定权限（Django 完整权限名 app_label.codename）。
    """
    # 校验权限名格式，必须为 app_label.codename
    if "." not in full_perm:
        raise ValueError("check_permission 需传入完整权限名，格式: app_label.codename，例如 'auth.view_user'")

    class _PermissionClass(BasePermission):
        def has_permission(self, request, view):
            # 无用户或未登录则拒绝
            if not request.user:
                return False
            if not request.user.is_authenticated:
                return False
            # 超级用户直接放行，不再校验具体权限
            if request.user.is_superuser:
                return True
            # 普通用户校验是否拥有指定权限
            return request.user.has_perm(full_perm)

    return permission_classes([_PermissionClass])
