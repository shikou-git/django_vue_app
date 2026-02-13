from django.db import models
from django.conf import settings


class ApiLog(models.Model):
    """接口访问日志：记录请求 path、method、状态码、用户、IP、User-Agent、时间"""

    path = models.CharField("请求路径", max_length=512, db_index=True)
    method = models.CharField("请求方法", max_length=16, db_index=True)
    status_code = models.PositiveIntegerField("HTTP 状态码", null=True, blank=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="api_logs",
        verbose_name="用户",
    )
    ip_address = models.GenericIPAddressField("IP 地址", null=True, blank=True, unpack_ipv4=True)
    user_agent = models.CharField("User-Agent", max_length=512, blank=True, default="")
    created_at = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "接口日志"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        permissions = [
            ("export_apilog", "导出接口日志"),
        ]

    def __str__(self):
        return f"{self.method} {self.path} {self.status_code}"
