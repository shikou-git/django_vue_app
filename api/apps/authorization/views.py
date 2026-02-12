# views.py
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Permission, Group
from django.db.models import Min
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authorization.filters import PermissionFilter, UserFilter
from apps.authorization.serializers import ChangePasswordSerializer, PermissionSerializer
from utils.custom_decorators import check_permission, skip_authentication, skip_permission
from utils.custom_response import Resp

# 默认密码
DEFAULT_PASSWORD = "123456"


# ==================== 工具函数 ====================


def _user_to_dict(user, include_permissions=False):
    """
    将 User 转为字典，包含 profile.real_name
    使用 getattr 兼容尚未创建 profile 的老用户
    时间字段转换为配置的时区（如 Asia/Shanghai）
    """
    profile = getattr(user, "profile", None)
    real_name = (profile.real_name or "").strip() if profile else ""

    date_joined_str = ""
    if user.date_joined:
        local_dt = timezone.localtime(user.date_joined)
        date_joined_str = local_dt.strftime("%Y-%m-%d %H:%M:%S")

    last_login_str = ""
    if user.last_login:
        local_dt = timezone.localtime(user.last_login)
        last_login_str = local_dt.strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "id": user.id,
        "username": user.username,
        "real_name": real_name,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "date_joined": date_joined_str,
        "last_login": last_login_str,
        "groups": [{"id": g.id, "name": g.name} for g in user.groups.all()],
    }
    if include_permissions:
        data["permissions"] = [{"id": p.id, "name": p.name, "codename": p.codename} for p in user.user_permissions.all()]
    return data


# ==================== 登录相关 ====================


@api_view(["POST"])
@skip_permission
@skip_authentication
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

    # 更新最后登录时间
    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])

    # 生成 JWT Token
    refresh = RefreshToken.for_user(user)

    return Resp.success(data={"access": str(refresh.access_token), "refresh": str(refresh)}, msg="登录成功")


@api_view(["POST"])
@skip_permission
@skip_authentication
def refresh_token(request):
    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Resp.bad_request(msg="refresh token 是必填项")

    try:
        refresh = RefreshToken(refresh_token)
        return Resp.success(data={"access": str(refresh.access_token), "refresh": str(refresh)}, msg="刷新成功")
    except Exception as e:
        return Resp.unauthorized(msg="无效的 refresh token")


@api_view(["POST"])
def user_logout(request):
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
def get_current_user(request):
    user = request.user
    profile = getattr(user, "profile", None)
    real_name = (profile.real_name or "").strip() if profile else ""
    roles = [{"id": g.id, "name": g.name} for g in user.groups.all()]

    return Resp.success(
        data={
            "id": user.id,
            "username": user.username,
            "real_name": real_name,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "roles": roles,
        },
        msg="获取成功",
    )


# ==================== 用户管理 ====================


@api_view(["POST"])
@check_permission("auth.view_user")
def get_user_list(request):
    data = request.data
    filter_params = {k: data[k] for k in UserFilter.base_filters if k in data}
    queryset = UserFilter(data=filter_params, queryset=User.objects.select_related("profile")).qs

    # 排序：支持 order_by 列表，如 ["username"]、["-date_joined"]；默认按工号升序
    order_by = data.get("order_by")
    if order_by and isinstance(order_by, list) and len(order_by) > 0:
        need_groups_annotate = any(
            isinstance(k, str) and k.lstrip("-") == "groups" for k in order_by
        )
        if need_groups_annotate:
            queryset = queryset.annotate(_group_sort=Min("groups__name")).distinct()
        order_fields = []
        for key in order_by:
            if not isinstance(key, str):
                continue
            desc = key.startswith("-")
            raw = key[1:] if desc else key
            if raw in UserFilter.ORDER_MAP:
                orm_field = UserFilter.ORDER_MAP[raw]
                order_fields.append("-" + orm_field if desc else orm_field)
            elif raw == "groups":
                order_fields.append("-_group_sort" if desc else "_group_sort")
        if order_fields:
            queryset = queryset.order_by(*order_fields)
        else:
            queryset = queryset.order_by("username")
    else:
        queryset = queryset.order_by("username")

    # 分页
    page = data.get("page", 1)
    page_size = data.get("page_size", 10)
    start = (page - 1) * page_size
    end = start + page_size

    total = queryset.count()
    users = queryset[start:end]

    results = [_user_to_dict(u) for u in users]

    return Resp.success(data={"results": results, "total": total, "page": page, "page_size": page_size}, msg="获取成功")


@api_view(["POST"])
@check_permission("auth.view_user")
def get_user_detail(request):
    user_id = request.data.get("user_id")

    if not user_id:
        return Resp.bad_request(msg="user_id 是必填项")

    try:
        user = User.objects.select_related("profile").get(id=user_id)
        return Resp.success(data=_user_to_dict(user, include_permissions=True), msg="获取成功")
    except User.DoesNotExist:
        return Resp.not_found(msg="用户不存在")


@api_view(["POST"])
@check_permission("auth.add_user")
def create_user(request):
    data = request.data

    username = data.get("username")
    password = data.get("password") or DEFAULT_PASSWORD

    if not username:
        return Resp.bad_request(msg="username 是必填项")
    if not password:
        return Resp.bad_request(msg="password 是必填项")

    if User.objects.filter(username=username).exists():
        return Resp.error(msg="用户名已存在", code=400)

    # 创建用户（signal 会自动创建 UserProfile）
    user = User.objects.create_user(
        username=username,
        password=password,
        email="",
        first_name="",
        last_name="",
        is_active=data.get("is_active", True),
        is_staff=False,
        is_superuser=False,
    )

    # 设置真实姓名
    real_name = (data.get("real_name") or "").strip()
    if real_name and getattr(user, "profile", None):
        user.profile.real_name = real_name
        user.profile.save()

    # 设置角色
    group_ids = data.get("group_ids", [])
    if group_ids:
        user.groups.set(group_ids)

    return Resp.success(data={"user_id": user.id}, msg="用户创建成功")


@api_view(["POST"])
@check_permission("auth.change_user")
def update_user(request):
    data = request.data
    user_id = data.get("user_id")

    if not user_id:
        return Resp.bad_request(msg="user_id 是必填项")

    try:
        user = User.objects.select_related("profile").get(id=user_id)
    except User.DoesNotExist:
        return Resp.not_found(msg="用户不存在")

    # 工号（username）唯一性检查
    if "username" in data:
        new_username = (data.get("username") or "").strip()
        if not new_username:
            return Resp.bad_request(msg="工号不能为空")
        if User.objects.filter(username=new_username).exclude(id=user.id).exists():
            return Resp.error(msg="工号已被其他用户使用", code=400)
        user.username = new_username

    # 可更新字段
    if "is_active" in data:
        user.is_active = data["is_active"]

    user.save()

    # 真实姓名写入 profile
    if "real_name" in data and getattr(user, "profile", None):
        user.profile.real_name = (data.get("real_name") or "").strip() or None
        user.profile.save()

    group_ids = data.get("group_ids")
    if group_ids is not None:
        user.groups.set(group_ids)

    return Resp.success(data=_user_to_dict(user), msg="更新成功")


@api_view(["POST"])
@check_permission("auth.delete_user")
def delete_user(request):
    user_id = request.data.get("user_id")

    if not user_id:
        return Resp.bad_request(msg="user_id 是必填项")

    if request.user.id == user_id:
        return Resp.forbidden(msg="不能删除当前登录用户")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Resp.not_found(msg="用户不存在")

    user.delete()
    return Resp.success(msg="删除成功")


@api_view(["POST"])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        errors = serializer.errors
        if "non_field_errors" in errors:
            msg = errors["non_field_errors"][0] if isinstance(errors["non_field_errors"], list) else str(errors["non_field_errors"])
        else:
            first_key = next(iter(errors))
            first_val = errors[first_key]
            msg = first_val[0] if isinstance(first_val, list) else str(first_val)
        return Resp.bad_request(msg=msg)

    user = request.user
    if not user.check_password(serializer.validated_data["old_password"]):
        return Resp.error(msg="原密码错误", code=400)

    user.set_password(serializer.validated_data["new_password"])
    user.save()
    return Resp.success(msg="密码修改成功")


@api_view(["POST"])
@check_permission("auth.change_user")
def reset_password(request):
    user_id = request.data.get("user_id")
    if not user_id:
        return Resp.bad_request(msg="user_id 是必填项")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Resp.not_found(msg="用户不存在")

    user.set_password(DEFAULT_PASSWORD)
    user.save()
    return Resp.success(msg="密码已重置为默认密码")


@api_view(["POST"])
@check_permission("auth.change_user")
def toggle_user_active(request):
    user_id = request.data.get("user_id")

    if not user_id:
        return Resp.bad_request(msg="user_id 是必填项")

    if request.user.id == user_id:
        return Resp.forbidden(msg="不能禁用当前登录用户")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Resp.not_found(msg="用户不存在")

    user.is_active = not user.is_active
    user.save()
    return Resp.success(
        data={"user_id": user.id, "is_active": user.is_active},
        msg="已" + ("启用" if user.is_active else "禁用") + "该用户",
    )


@api_view(["POST"])
@check_permission("auth.view_user")
def get_group_list(request):
    groups = Group.objects.all().order_by("name")
    results = [{"id": g.id, "name": g.name} for g in groups]
    return Resp.success(data={"results": results, "total": len(results)}, msg="获取成功")


# ==================== 权限管理 ====================


@api_view(["POST"])
@check_permission("auth.view_permission")
def get_permission_filter_options(request):
    """返回权限列表筛选项：app_labels、models（用于表格列筛选下拉）"""
    from django.contrib.contenttypes.models import ContentType

    ct_with_perm = ContentType.objects.filter(permission__isnull=False)
    app_labels = list(ct_with_perm.values_list("app_label", flat=True).distinct().order_by("app_label"))
    models = list(ct_with_perm.values_list("model", flat=True).distinct().order_by("model"))
    return Resp.success(data={"app_labels": app_labels, "models": models}, msg="获取成功")


@api_view(["POST"])
@check_permission("auth.view_permission")
def get_permission_list(request):
    data = request.data
    filter_params = {k: data[k] for k in PermissionFilter.base_filters if k in data}
    queryset = PermissionFilter(data=filter_params, queryset=Permission.objects.select_related("content_type")).qs

    # 排序：支持 order_by 列表，如 ["app_label", "-codename"]，只接受允许的字段
    order_by = data.get("order_by")
    if order_by is not None and isinstance(order_by, list) and len(order_by) > 0:
        order_fields = []
        for key in order_by:
            if not isinstance(key, str):
                continue
            desc = key.startswith("-")
            raw = key[1:] if desc else key
            if raw in PermissionFilter.ORDER_MAP:
                orm_field = PermissionFilter.ORDER_MAP[raw]
                order_fields.append("-" + orm_field if desc else orm_field)
        if order_fields:
            queryset = queryset.order_by(*order_fields)
        else:
            queryset = queryset.order_by("content_type__app_label", "content_type__model", "codename")
    else:
        queryset = queryset.order_by("content_type__app_label", "content_type__model", "codename")

    page = data.get("page", 1)
    page_size = data.get("page_size", 10)
    start = (page - 1) * page_size
    end = start + page_size

    total = queryset.count()
    permissions = queryset[start:end]
    serializer = PermissionSerializer(permissions, many=True)

    return Resp.success(data={"results": serializer.data, "total": total, "page": page, "page_size": page_size}, msg="获取成功")


@api_view(["POST"])
@check_permission("auth.view_permission")
def get_permission_detail(request):
    permission_id = request.data.get("permission_id")

    if not permission_id:
        return Resp.bad_request(msg="permission_id 是必填项")

    try:
        perm = Permission.objects.select_related("content_type").get(id=permission_id)
        serializer = PermissionSerializer(perm)
        return Resp.success(data=serializer.data, msg="获取成功")
    except Permission.DoesNotExist:
        return Resp.not_found(msg="权限不存在")
