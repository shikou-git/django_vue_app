# views.py
import time
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Permission, Group
from django.core.cache import cache
from django.db.models import Min
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authorization.filters import PermissionFilter, UserFilter
from apps.authorization.serializers import ChangePasswordSerializer, GroupSerializer, PermissionSerializer
from utils.const import (
    DEFAULT_PASSWORD,
    LOGIN_FAILURE_WINDOW_SECONDS,
    LOGIN_LOCKOUT_SECONDS,
    LOGIN_MAX_FAILURES,
    LOGIN_PUNISHMENT_TYPE,
)
from utils.custom_decorators import check_permission, skip_authentication, skip_permission
from utils.custom_response import Resp


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
        data["permissions"] = [
            {"id": p.id, "name": p.name, "codename": p.codename} for p in user.user_permissions.all()
        ]
    return data


# ==================== 登录相关 ====================


def _login_lockout_config():
    """登录锁定相关配置（来自 utils.const）"""
    return {
        "window_seconds": LOGIN_FAILURE_WINDOW_SECONDS,
        "max_failures": LOGIN_MAX_FAILURES,
        "punishment_type": LOGIN_PUNISHMENT_TYPE,
        "lockout_seconds": LOGIN_LOCKOUT_SECONDS,
    }


@api_view(["POST"])
@skip_permission
@skip_authentication
def user_login(request):
    """
    用户登录 - 使用 JWT 认证
    支持：指定时间内失败次数达到阈值则锁定（可配置惩罚方式与解锁时间）。
    POST /api/auth/login/
    {"username": "admin", "password": "password"}
    返回: {"msg": "登录成功", "code": 0, "data": {"access": "...", "refresh": "...", "user": {...}}}
    """
    username = (request.data.get("username") or "").strip()
    password = request.data.get("password")

    if not username or not password:
        return Resp.bad_request(msg="用户名和密码不能为空")

    cfg = _login_lockout_config()
    window_seconds = cfg["window_seconds"]
    max_failures = cfg["max_failures"]
    punishment_type = cfg["punishment_type"]
    lockout_seconds = cfg["lockout_seconds"]

    cache_key_locked = f"login_locked:{username}"
    cache_key_failures = f"login_failures:{username}"
    now_ts = time.time()

    # 1) 检查是否处于冷却中（仅 cooldown 模式会设置；disable 模式不设冷却，账户需管理员恢复）
    locked_until = cache.get(cache_key_locked)
    if locked_until is not None and now_ts < locked_until:
        remaining = int(locked_until - now_ts)
        return Resp.forbidden(
            msg=f"登录失败次数过多，请 {remaining} 秒（约 { (remaining + 59) // 60 } 分钟）后再试",
            data={"lockout_seconds_remaining": remaining},
        )

    try:
        user_by_name = User.objects.get(username=username)
    except User.DoesNotExist:
        user_by_name = None

    # 2) 账户被禁用时直接拒绝（含因失败次数过多被禁用的情况，需管理员在用户管理中恢复）
    if user_by_name and not user_by_name.is_active:
        return Resp.forbidden(msg="该账户已被禁用，请联系管理员恢复")

    # 3) 获取/刷新失败记录（超出时间窗口则重新计数）
    failure_record = cache.get(cache_key_failures) or {"count": 0, "first_at": now_ts}
    first_at = failure_record.get("first_at", now_ts)
    if now_ts - first_at > window_seconds:
        failure_record = {"count": 0, "first_at": now_ts}
    count = failure_record.get("count", 0)

    # 4) 验证用户名和密码
    user = authenticate(username=username, password=password)

    if not user:
        count += 1
        failure_record["count"] = count
        failure_record["first_at"] = failure_record.get("first_at", now_ts)
        cache.set(cache_key_failures, failure_record, timeout=window_seconds + 60)

        if count >= max_failures:
            cache.delete(cache_key_failures)
            if punishment_type == "disable" and user_by_name:
                user_by_name.is_active = False
                user_by_name.save(update_fields=["is_active"])
                return Resp.forbidden(msg="登录失败次数过多，账户已禁用，请联系管理员恢复")
            locked_until = now_ts + lockout_seconds
            cache.set(cache_key_locked, locked_until, timeout=lockout_seconds + 60)
            return Resp.forbidden(
                msg=f"登录失败次数过多，请 {lockout_seconds} 秒（约 { (lockout_seconds + 59) // 60 } 分钟）后再试",
                data={"lockout_seconds_remaining": lockout_seconds},
            )
        return Resp.unauthorized(msg="用户名或密码错误")

    # 5) 登录成功：清除失败记录与冷却标记
    cache.delete(cache_key_failures)
    cache.delete(cache_key_locked)

    if not user.is_active:
        return Resp.forbidden(msg="该账户已被禁用")

    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])

    refresh = RefreshToken.for_user(user)
    return Resp.success(
        data={"access": str(refresh.access_token), "refresh": str(refresh)},
        msg="登录成功",
    )


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
    # 当前用户拥有的权限列表（完整权限名，如 auth.add_user），供前端控制按钮禁用等
    permissions = list(user.get_all_permissions()) if user.is_authenticated else []

    return Resp.success(
        data={
            "id": user.id,
            "username": user.username,
            "real_name": real_name,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "roles": roles,
            "permissions": permissions,
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
        need_groups_annotate = any(isinstance(k, str) and k.lstrip("-") == "groups" for k in order_by)
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
    """仅允许修改当前登录用户自己的密码（不接收 user_id，只操作 request.user）。"""
    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        errors = serializer.errors
        if "non_field_errors" in errors:
            msg = (
                errors["non_field_errors"][0]
                if isinstance(errors["non_field_errors"], list)
                else str(errors["non_field_errors"])
            )
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


# ==================== 角色管理 ====================


@api_view(["POST"])
@check_permission("auth.view_group")
def get_group_list(request):
    """
    角色列表。不传 page/page_size 时返回全部（供下拉等用）；传则分页并支持 search 按名称搜索。
    """
    data = request.data or {}
    queryset = Group.objects.all().order_by("name")

    search = (data.get("search") or "").strip()
    if search:
        queryset = queryset.filter(name__icontains=search)

    page = data.get("page")
    page_size = data.get("page_size")
    if page is not None and page_size is not None:
        page = max(1, int(page))
        page_size = max(1, min(int(page_size), 100))
        start = (page - 1) * page_size
        end = start + page_size
        total = queryset.count()
        groups = queryset[start:end]
        results = [
            {"id": g.id, "name": g.name, "user_count": g.user_set.count(), "permission_count": g.permissions.count()}
            for g in groups
        ]
        return Resp.success(
            data={"results": results, "total": total, "page": page, "page_size": page_size}, msg="获取成功"
        )

    results = [{"id": g.id, "name": g.name} for g in queryset]
    return Resp.success(data={"results": results, "total": len(results)}, msg="获取成功")


@api_view(["POST"])
@check_permission("auth.view_group")
def get_group_detail(request):
    group_id = request.data.get("group_id")
    if not group_id:
        return Resp.bad_request(msg="group_id 是必填项")
    try:
        group = Group.objects.prefetch_related("permissions").get(id=group_id)
        ser = GroupSerializer(group)
        data = dict(ser.data)
        data["permission_ids"] = list(group.permissions.values_list("id", flat=True))
        return Resp.success(data=data, msg="获取成功")
    except Group.DoesNotExist:
        return Resp.not_found(msg="角色不存在")


@api_view(["POST"])
@check_permission("auth.add_group")
def create_group(request):
    data = request.data
    name = (data.get("name") or "").strip()
    if not name:
        return Resp.bad_request(msg="角色名称不能为空")
    if Group.objects.filter(name=name).exists():
        return Resp.error(msg="角色名称已存在", code=400)
    group = Group.objects.create(name=name)
    permission_ids = data.get("permission_ids")
    if permission_ids is not None and isinstance(permission_ids, list) and len(permission_ids) > 0:
        group.permissions.set(permission_ids)
    return Resp.success(data={"group_id": group.id}, msg="创建成功")


@api_view(["POST"])
@check_permission("auth.change_group")
def update_group(request):
    data = request.data
    group_id = data.get("group_id")
    if not group_id:
        return Resp.bad_request(msg="group_id 是必填项")
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Resp.not_found(msg="角色不存在")
    name = data.get("name")
    if name is not None:
        name = (name or "").strip()
        if not name:
            return Resp.bad_request(msg="角色名称不能为空")
        if Group.objects.filter(name=name).exclude(id=group.id).exists():
            return Resp.error(msg="角色名称已存在", code=400)
        group.name = name
        group.save()
    permission_ids = data.get("permission_ids")
    if permission_ids is not None:
        group.permissions.set(permission_ids if isinstance(permission_ids, list) else [])
    return Resp.success(data={"id": group.id, "name": group.name}, msg="更新成功")


@api_view(["POST"])
@check_permission("auth.delete_group")
def delete_group(request):
    group_id = request.data.get("group_id")
    if not group_id:
        return Resp.bad_request(msg="group_id 是必填项")
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Resp.not_found(msg="角色不存在")
    group.delete()
    return Resp.success(msg="删除成功")


# ==================== 用户角色管理 ====================


@api_view(["POST"])
@check_permission("auth.change_user")
def add_user_to_group(request):
    """将用户加入角色。POST: user_id, group_id"""
    user_id = request.data.get("user_id")
    group_id = request.data.get("group_id")
    if not user_id:
        return Resp.bad_request(msg="user_id 是必填项")
    if not group_id:
        return Resp.bad_request(msg="group_id 是必填项")
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Resp.not_found(msg="用户不存在")
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Resp.not_found(msg="角色不存在")
    if user.groups.filter(id=group_id).exists():
        return Resp.success(msg="用户已在该角色中", data={"user_id": user.id, "group_id": group.id})
    user.groups.add(group)
    return Resp.success(msg="已加入角色", data={"user_id": user.id, "group_id": group.id})


@api_view(["POST"])
@check_permission("auth.change_user")
def remove_user_from_group(request):
    """将用户移出角色。POST: user_id, group_id"""
    user_id = request.data.get("user_id")
    group_id = request.data.get("group_id")
    if not user_id:
        return Resp.bad_request(msg="user_id 是必填项")
    if not group_id:
        return Resp.bad_request(msg="group_id 是必填项")
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Resp.not_found(msg="用户不存在")
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Resp.not_found(msg="角色不存在")
    user.groups.remove(group)
    return Resp.success(msg="已移出角色", data={"user_id": user.id, "group_id": group.id})


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

    return Resp.success(
        data={"results": serializer.data, "total": total, "page": page, "page_size": page_size}, msg="获取成功"
    )


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
