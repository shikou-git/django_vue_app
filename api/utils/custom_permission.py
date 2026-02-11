from rest_framework.permissions import BasePermission


# ==================== 自定义权限类 ====================


class IsAdminUser(BasePermission):
    """
    自定义权限：要求用户是管理员（staff 或 superuser）
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
