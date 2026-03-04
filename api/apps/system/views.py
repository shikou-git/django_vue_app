from rest_framework.decorators import api_view

from apps.system.models import BaseSetting
from utils.custom_decorators import check_permission
from utils.custom_response import Resp


@api_view(["POST"])
def get_base_settings(request):
    """
    获取基本设置（公告内容与开关）。
    任意登录用户可读，用于 Header 展示公告。
    """
    setting = BaseSetting.load()
    return Resp.success(
        data={
            "announcement_content": setting.announcement_content or "",
            "announcement_enabled": setting.announcement_enabled,
        },
        msg="获取成功",
    )


@api_view(["POST"])
@check_permission("system.change_basesetting")
def update_base_settings(request):
    """
    更新基本设置（公告内容、公告开关）。
    需要权限：system.change_basesetting（修改基本设置）。
    """
    data = request.data
    announcement_content = data.get("announcement_content")
    announcement_enabled = data.get("announcement_enabled")

    setting = BaseSetting.load()
    if announcement_content is not None:
        setting.announcement_content = announcement_content if isinstance(announcement_content, str) else ""
    if announcement_enabled is not None:
        setting.announcement_enabled = bool(announcement_enabled)
    setting.save()

    return Resp.success(
        data={
            "announcement_content": setting.announcement_content or "",
            "announcement_enabled": setting.announcement_enabled,
        },
        msg="保存成功",
    )
