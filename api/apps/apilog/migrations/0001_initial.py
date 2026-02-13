# Generated manually for ApiLog model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ApiLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("path", models.CharField(db_index=True, max_length=512, verbose_name="请求路径")),
                ("method", models.CharField(db_index=True, max_length=16, verbose_name="请求方法")),
                ("status_code", models.PositiveIntegerField(blank=True, db_index=True, null=True, verbose_name="HTTP 状态码")),
                ("user_agent", models.CharField(blank=True, default="", max_length=512, verbose_name="User-Agent")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="创建时间")),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True, unpack_ipv4=True, verbose_name="IP 地址")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="api_logs", to=settings.AUTH_USER_MODEL, verbose_name="用户")),
            ],
            options={
                "verbose_name": "接口日志",
                "verbose_name_plural": "接口日志",
                "ordering": ["-created_at"],
                "permissions": [("export_apilog", "导出接口日志")],
            },
        ),
    ]
