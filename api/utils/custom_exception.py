"""
全局异常处理
统一捕获 DRF 视图中的异常，返回项目标准格式 {"code": x, "msg": "...", "data": {}}
"""

import re

from django.conf import settings
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from utils.custom_logger import logger
from utils.custom_response import Resp


def custom_exception_handler(exc, context):
    """
    全局异常处理器
    - 先调用 DRF 默认处理器处理已知异常
    - 将响应格式化为项目统一格式
    - 兜底捕获未处理异常，避免 500 裸错误
    """
    # 1. 调用 DRF 默认处理器
    response = drf_exception_handler(exc, context)

    if response is not None:
        # DRF 已处理，转换为项目统一格式
        return _format_drf_response(response)
    else:
        # 2. DRF 未处理的异常，手动处理
        return _handle_unhandled_exception(exc, context)


def _format_drf_response(response):
    """将 DRF 默认响应格式转为项目统一格式"""
    data = response.data
    if isinstance(data, dict) and "code" not in data:
        # 限流 429：返回中文提示
        if response.status_code == 429:
            detail = data.get("detail", "")
            if isinstance(detail, str) and "available" in detail.lower():
                m = re.search(r"(\d+)\s*second", detail, re.I)
                msg = f"请求过于频繁，请 {m.group(1)} 秒后再试" if m else "请求过于频繁，请稍后再试"
            else:
                msg = "请求过于频繁，请稍后再试"
            return Response(
                {"code": 429, "msg": msg, "data": {}},
                status=429,
            )
        # 提取 msg：detail 或 ValidationError 的字段级错误
        msg = data.get("detail")
        if msg is None:
            # ValidationError: {"field": ["err1"]} 或 {"field": "err"}
            parts = []
            for k, v in data.items():
                if isinstance(v, list):
                    parts.append(f"{k}: {v[0]}" if v else f"{k}: 错误")
                else:
                    parts.append(f"{k}: {v}")
            msg = "; ".join(parts) if parts else "请求错误"
        elif isinstance(msg, list):
            msg = msg[0] if msg else "请求错误"
        elif isinstance(msg, dict):
            msg = "; ".join(f"{k}: {v}" for k, v in msg.items()) if msg else "请求错误"
        return Response(
            {"code": response.status_code, "msg": str(msg), "data": {}},
            status=response.status_code,
        )
    return response


def _handle_unhandled_exception(exc, context):
    """处理 DRF 未捕获的异常"""
    request = context.get("request")
    view = context.get("view")

    # Django 常见异常
    if isinstance(exc, Http404):
        return Resp.not_found(msg="资源不存在")
    if isinstance(exc, DjangoPermissionDenied):
        return Resp.forbidden(msg="无权访问")

    # 兜底：记录日志并返回 500
    logger.exception(
        "未处理的异常: %s, view=%s, request=%s",
        exc,
        view.__class__.__name__ if view else "unknown",
        request.path if request else "unknown",
    )
    return Resp.server_error(
        msg="服务器内部错误" if not getattr(settings, "DEBUG", False) else str(exc),
    )
