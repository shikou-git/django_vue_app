from django.db import models


class BaseSetting(models.Model):
    """
    基本设置（单例：仅一条记录，用于公告等全局配置）。
    通过该模型挂载 Django 权限，便于为「基本设置」分配 system.change_basesetting。
    """
    announcement_content = models.TextField("公告内容", blank=True, default="")
    announcement_enabled = models.BooleanField("公告开关", default=False)

    class Meta:
        verbose_name = "基本设置"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        # 单例：只保留一条记录
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={"announcement_content": "", "announcement_enabled": False})
        return obj
