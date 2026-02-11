# utils/decorators.py - 权限白名单与鉴权装饰器
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, BasePermission


def skip_permission(func):
    return permission_classes([AllowAny])(func)


def skip_authentication(func):
    return authentication_classes([])(func)


def check_permission(full_perm):
    """
    接口鉴权装饰器：要求当前用户拥有指定权限（Django 完整权限名 app_label.codename）。

    - 支持模型默认 4 种权限：auth.add_user, auth.change_user, auth.delete_user, auth.view_user
    - 支持自定义权限：如 auth.export_user, auth.import_user（需在后台或迁移中创建对应 Permission）

    用法:
        @check_permission('auth.view_user')
        @check_permission('auth.add_user')
        @check_permission('auth.export_user')
        @check_permission('content.export_article')
    """
    if "." not in full_perm:
        raise ValueError("check_permission 需传入完整权限名，格式: app_label.codename，例如 'auth.view_user'")

    class _PermissionClass(BasePermission):
        def has_permission(self, request, view):
            if not request.user:
                return False
            if not request.user.is_authenticated:
                return False
            return request.user.has_perm(full_perm)

    return permission_classes([_PermissionClass])
