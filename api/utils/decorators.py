# utils/decorators.py - 权限白名单装饰器
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny


def skip_permission(func):
    return permission_classes([AllowAny])(func)


def skip_authentication(func):
    return authentication_classes([])(func)
