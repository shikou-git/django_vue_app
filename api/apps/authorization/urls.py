# urls.py
from django.urls import path

from . import views

urlpatterns = [
    # ==================== 登录接口 ====================
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("refresh_token/", views.refresh_token, name="refresh_token"),
    path("get_current_user/", views.get_current_user, name="get_current_user"),
    # # ==================== 用户管理接口 ====================
    path("get_user_list/", views.get_user_list, name="get_user_list"),
    path("get_user_detail/", views.get_user_detail, name="get_user_detail"),
    path("create_user/", views.create_user, name="create_user"),
    path("update_user/", views.update_user, name="update_user"),
    path("delete_user/", views.delete_user, name="delete_user"),
    path("change_password/", views.change_password, name="change_password"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path("toggle_user_active/", views.toggle_user_active, name="toggle_user_active"),
    path("get_group_list/", views.get_group_list, name="get_group_list"),
    # # ==================== 角色管理接口 ====================
    # path("get_group_detail/", views.get_group_detail, name="get_group_detail"),
    # path("create_group/", views.create_group, name="create_group"),
    # path("update_group/", views.update_group, name="update_group"),
    # path("delete_group/", views.delete_group, name="delete_group"),
    # path("add_user_to_group/", views.add_user_to_group, name="add_user_to_group"),
    # path("remove_user_from_group/", views.remove_user_from_group, name="remove_user_from_group"),
    # # ==================== 权限管理接口 ====================
    path("get_permission_list/", views.get_permission_list, name="get_permission_list"),
    path("get_permission_detail/", views.get_permission_detail, name="get_permission_detail"),
    path("create_permission/", views.create_permission, name="create_permission"),
    path("update_permission/", views.update_permission, name="update_permission"),
    path("delete_permission/", views.delete_permission, name="delete_permission"),
    path("get_content_type_list/", views.get_content_type_list, name="get_content_type_list"),
    # # ==================== 用户权限管理 ====================
    # path("get_user_permissions/", views.get_user_permissions, name="get_user_permissions"),
    # path("add_permission_to_user/", views.add_permission_to_user, name="add_permission_to_user"),
    # path("remove_permission_from_user/", views.remove_permission_from_user, name="remove_permission_from_user"),
    # # ==================== 角色权限管理 ====================
    # path("get_group_permissions/", views.get_group_permissions, name="get_group_permissions"),
    # path("add_permission_to_group/", views.add_permission_to_group, name="add_permission_to_group"),
    # path("remove_permission_from_group/", views.remove_permission_from_group, name="remove_permission_from_group"),
]
