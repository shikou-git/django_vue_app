"""
用户权限管理视图
使用 Django REST Framework + JWT 认证，所有接口统一 POST 方法
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from utils.custom_response import Resp



# ==================== 登录相关 ====================


@api_view(["POST"])
@permission_classes([AllowAny])
def user_login(request):
    """
    用户登录 - 使用 JWT 认证
    POST /api/auth/login/
    {"username": "admin", "password": "password"}
    返回: {"msg": "登录成功", "code": 0, "data": {"access": "...", "refresh": "...", "user": {...}}}
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Resp.bad_request(msg="用户名和密码不能为空")

    # 验证用户名和密码
    user = authenticate(username=username, password=password)

    if not user:
        return Resp.unauthorized(msg="用户名或密码错误")

    if not user.is_active:
        return Resp.forbidden(msg="该账户已被禁用")

    # 生成 JWT Token
    refresh = RefreshToken.for_user(user)

    return Resp.success(
        data={
            "access": str(refresh.access_token),  # Access Token（短期有效）
            "refresh": str(refresh),  # Refresh Token（用于刷新 Access Token）
        },
        msg="登录成功",
    )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """
    用户登出 - JWT 无状态，客户端删除 Token 即可
    POST /api/auth/logout/
    请求头: Authorization: Bearer <access_token>
    返回: {"msg": "登出成功", "code": 0, "data": {}}

    可选：如果需要实现黑名单，可以将 refresh_token 加入黑名单
    """
    try:
        # JWT 是无状态的，登出只需要客户端删除 token
        # 如果传入了 refresh token，可以将其加入黑名单（需要启用 BLACKLIST）
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()  # 需要安装 rest_framework_simplejwt.token_blacklist
    except Exception:
        pass

    return Resp.success(msg="登出成功")


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    获取当前用户信息
    POST /api/auth/get-current-user/
    请求头: Authorization: Bearer <access_token>
    返回: {"msg": "获取成功", "code": 0, "data": {...}}
    """
    user = request.user
    roles = [{"id": g.id, "name": g.name} for g in user.groups.all()]

    return Resp.success(
        data={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "roles": roles,
        },
        msg="获取成功",
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    刷新 Access Token
    POST /api/auth/refresh-token/
    {"refresh": "<refresh_token>"}
    返回: {"msg": "刷新成功", "code": 0, "data": {"access": "...", "refresh": "..."}}
    """
    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Resp.bad_request(msg="refresh token 是必填项")

    try:
        refresh = RefreshToken(refresh_token)
        # 生成新的 access token
        return Resp.success(
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),  # 如果启用了 ROTATE_REFRESH_TOKENS，会返回新的 refresh token
            },
            msg="刷新成功",
        )
    except Exception as e:
        return Resp.unauthorized(msg="无效的 refresh token")


# ==================== 用户管理 ====================


# @api_view(["POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def get_user_list(request):
#     """
#     获取用户列表
#     POST /api/auth/get-user-list/
#     {"page": 1, "page_size": 10, "search": "", "is_active": true}
#     """
#     data = request.data
#     queryset = User.objects.all().order_by("-date_joined")

#     # 搜索
#     search = data.get("search", "").strip()
#     if search:
#         queryset = queryset.filter(
#             Q(username__icontains=search) | Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)
#         )

#     # 筛选
#     if data.get("is_active") is not None:
#         queryset = queryset.filter(is_active=data["is_active"])
#     if data.get("is_staff") is not None:
#         queryset = queryset.filter(is_staff=data["is_staff"])
#     if data.get("is_superuser") is not None:
#         queryset = queryset.filter(is_superuser=data["is_superuser"])
#     if data.get("group"):
#         queryset = queryset.filter(groups__id=data["group"])

#     # 分页
#     page = data.get("page", 1)
#     page_size = data.get("page_size", 10)
#     start = (page - 1) * page_size
#     end = start + page_size

#     total = queryset.count()
#     users = queryset[start:end]

#     results = []
#     for user in users:
#         results.append(
#             {
#                 "id": user.id,
#                 "username": user.username,
#                 "email": user.email,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#                 "is_active": user.is_active,
#                 "is_staff": user.is_staff,
#                 "is_superuser": user.is_superuser,
#                 "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
#                 "groups": [{"id": g.id, "name": g.name} for g in user.groups.all()],
#             }
#         )

#     return Response({"results": results, "total": total, "page": page, "page_size": page_size})


# @api_view(["POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def get_user_detail(request):
#     """
#     获取用户详情
#     POST /api/auth/get-user-detail/
#     {"user_id": 1}
#     """
#     user_id = request.data.get("user_id")

#     if not user_id:
#         return Response({"error": "user_id 是必填项"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         user = User.objects.get(id=user_id)
#         return Response(
#             {
#                 "id": user.id,
#                 "username": user.username,
#                 "email": user.email,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#                 "is_active": user.is_active,
#                 "is_staff": user.is_staff,
#                 "is_superuser": user.is_superuser,
#                 "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
#                 "groups": [{"id": g.id, "name": g.name} for g in user.groups.all()],
#                 "permissions": [{"id": p.id, "name": p.name, "codename": p.codename} for p in user.user_permissions.all()],
#             }
#         )
#     except User.DoesNotExist:
#         return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)


# @api_view(["POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def create_user(request):
#     """
#     创建用户
#     POST /api/auth/create-user/
#     {"username": "test", "password": "123456", "email": "test@example.com", "group_ids": [1,2]}
#     """
#     data = request.data

#     username = data.get("username")
#     password = data.get("password")
#     email = data.get("email", "")

#     if not username:
#         return Response({"error": "username 是必填项"}, status=status.HTTP_400_BAD_REQUEST)
#     if not password:
#         return Response({"error": "password 是必填项"}, status=status.HTTP_400_BAD_REQUEST)

#     if User.objects.filter(username=username).exists():
#         return Response({"error": "用户名已存在"}, status=status.HTTP_400_BAD_REQUEST)

#     # 创建用户
#     user = User.objects.create_user(
#         username=username,
#         password=password,
#         email=email,
#         first_name=data.get("first_name", ""),
#         last_name=data.get("last_name", ""),
#         is_active=data.get("is_active", True),
#         is_staff=data.get("is_staff", False),
#         is_superuser=data.get("is_superuser", False),
#     )

#     # 设置角色
#     group_ids = data.get("group_ids", [])
#     if group_ids:
#         user.groups.set(group_ids)

#     return Response({"message": "用户创建成功", "user_id": user.id})


# @api_view(["POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def update_user(request):
#     """
#     更新用户
#     POST /api/auth/update-user/
#     {"user_id": 1, "email": "new@example.com", "group_ids": [1,2]}
#     """
#     data = request.data
#     user_id = data.get("user_id")

#     if not user_id:
#         return Response({"error": "user_id 是必填项"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         user = User.objects.get(id=user_id)

#         # 更新字段
#         if "email" in data:
#             user.email = data["email"]
#         if "first_name" in data:
#             user.first_name = data["first_name"]
#         if "last_name" in data:
#             user.last_name = data["last_name"]
#         if "is_active" in data:
#             user.is_active = data["is_active"]
#         if "is_staff" in data:
#             user.is_staff = data["is_staff"]
#         if "is_superuser" in data:
#             user.is_superuser = data["is_superuser"]

#         user.save()

#         # 更新角色
#         if "group_ids" in data:
#             user.groups.set(data["group_ids"])

#         return Response({"message": "用户更新成功"})
#     except User.DoesNotExist:
#         return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)


# @api_view(["POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def delete_user(request):
#     """
#     删除用户
#     POST /api/auth/delete-user/
#     {"user_id": 1}
#     """
#     user_id = request.data.get("user_id")

#     if not user_id:
#         return Response({"error": "user_id 是必填项"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         user = User.objects.get(id=user_id)
#         username = user.username
#         user.delete()
#         return Response({"message": f"用户 {username} 已删除"})
#     except User.DoesNotExist:
#         return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)


# @api_view(["POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def change_password(request):
#     """
#     修改密码
#     POST /api/auth/change-password/
#     {"user_id": 1, "old_password": "123", "new_password": "456"}
#     """
#     data = request.data
#     user_id = data.get("user_id")
#     old_password = data.get("old_password")
#     new_password = data.get("new_password")

#     if not user_id:
#         return Response({"error": "user_id 是必填项"}, status=status.HTTP_400_BAD_REQUEST)
#     if not old_password:
#         return Response({"error": "old_password 是必填项"}, status=status.HTTP_400_BAD_REQUEST)
#     if not new_password:
#         return Response({"error": "new_password 是必填项"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         user = User.objects.get(id=user_id)
#         if not user.check_password(old_password):
#             return Response({"error": "旧密码错误"}, status=status.HTTP_400_BAD_REQUEST)

#         user.set_password(new_password)
#         user.save()
#         return Response({"message": "密码修改成功"})
#     except User.DoesNotExist:
#         return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)


# @api_view(["POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def reset_password(request):
#     """
#     重置密码（管理员）
#     POST /api/auth/reset-password/
#     {"user_id": 1, "new_password": "123456"}
#     """
#     data = request.data
#     user_id = data.get("user_id")
#     new_password = data.get("new_password")

#     if not user_id:
#         return Response({"error": "user_id 是必填项"}, status=status.HTTP_400_BAD_REQUEST)
#     if not new_password:
#         return Response({"error": "new_password 是必填项"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         user = User.objects.get(id=user_id)
#         user.set_password(new_password)
#         user.save()
#         return Response({"message": "密码重置成功"})
#     except User.DoesNotExist:
#         return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)


# @api_view(["POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def toggle_user_active(request):
#     """
#     切换用户激活状态
#     POST /api/auth/toggle-user-active/
#     {"user_id": 1}
#     """
#     user_id = request.data.get("user_id")

#     if not user_id:
#         return Response({"error": "user_id 是必填项"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         user = User.objects.get(id=user_id)
#         user.is_active = not user.is_active
#         user.save()
#         return Response({"message": f'用户已{"激活" if user.is_active else "禁用"}', "is_active": user.is_active})
#     except User.DoesNotExist:
#         return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
