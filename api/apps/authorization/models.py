# models.py
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    用户扩展信息（Profile 模式）
    通过 OneToOneField 关联 User，不修改 Django 原生 User 模型
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    real_name = models.CharField("真实姓名", max_length=64, blank=True, null=True, db_comment="真实姓名")

    class Meta:
        verbose_name = "用户扩展信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """用户创建时自动创建 UserProfile"""
    if created:
        UserProfile.objects.get_or_create(user=instance)
