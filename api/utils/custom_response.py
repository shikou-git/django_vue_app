"""
统一响应格式封装
使用方式：
    - Resp.success(data={"user": "admin"}, msg="操作成功")
    - Resp.error(msg="参数错误", code=400)
    - Resp.custom(msg="自定义消息", data={}, code=200)
"""

from rest_framework.response import Response
from rest_framework import status


class Resp:
    """统一响应格式类"""

    @staticmethod
    def success(data=None, msg="操作成功", code=0):
        """成功响应"""
        return Response(
            {"code": code, "msg": msg, "data": data if data is not None else {}},
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def error(msg="操作失败", data=None, code=1):
        """错误响应"""
        return Response(
            {"code": code, "msg": msg, "data": data if data is not None else {}},
            status=status.HTTP_200_OK,  # HTTP 状态码仍为 200，业务错误通过 code 区分
        )

    @staticmethod
    def custom(msg="", data=None, code=200, http_status=None):
        """自定义响应"""
        return Response(
            {"code": code, "msg": msg, "data": data if data is not None else {}},
            status=http_status if http_status else status.HTTP_200_OK,
        )

    @staticmethod
    def bad_request(msg="请求参数错误", data=None):
        """请求参数错误响应（400）"""
        return Response(
            {"code": 400, "msg": msg, "data": data if data is not None else {}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @staticmethod
    def unauthorized(msg="未授权", data=None):
        """未授权响应（401）"""
        return Response(
            {"code": 401, "msg": msg, "data": data if data is not None else {}},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def forbidden(msg="无权限", data=None):
        """禁止访问响应（403）"""
        return Response(
            {"code": 403, "msg": msg, "data": data if data is not None else {}},
            status=status.HTTP_403_FORBIDDEN,
        )

    @staticmethod
    def not_found(msg="资源不存在", data=None):
        """资源不存在响应（404）"""
        return Response(
            {"code": 404, "msg": msg, "data": data if data is not None else {}},
            status=status.HTTP_404_NOT_FOUND,
        )

    @staticmethod
    def server_error(msg="服务器内部错误", data=None):
        """服务器错误响应（500）"""
        return Response(
            {"code": 500, "msg": msg, "data": data if data is not None else {}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
