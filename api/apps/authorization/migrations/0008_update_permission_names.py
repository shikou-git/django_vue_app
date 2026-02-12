# 数据迁移：更新权限的显示名称（name）
# Django 的 AlterModelOptions 只负责“创建”权限，不会更新已存在权限的 name

from django.db import migrations


def update_permission_names(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    ct = ContentType.objects.get(app_label="authorization", model="userprofile")
    updates = [
        ("export_user", "导出用户"),
        ("import_user", "导入用户"),
    ]
    for codename, name in updates:
        Permission.objects.filter(content_type=ct, codename=codename).update(name=name)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("authorization", "0007_alter_userprofile_options"),
    ]

    operations = [
        migrations.RunPython(update_permission_names, noop),
    ]
