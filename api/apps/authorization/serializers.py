"""
用户权限管理序列化器
基于 Django auth 的 User, Group, Permission 模型
"""
from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""

    content_type_name = serializers.CharField(source="content_type.model", read_only=True)

    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "content_type", "content_type_name"]
        read_only_fields = ["id"]


class PermissionSimpleSerializer(serializers.ModelSerializer):
    """权限简化序列化器（用于嵌套显示）"""

    class Meta:
        model = Permission
        fields = ["id", "name", "codename"]


class GroupSerializer(serializers.ModelSerializer):
    """角色/组序列化器"""

    permissions = PermissionSimpleSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(many=True, write_only=True, queryset=Permission.objects.all(), source="permissions")
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "name", "permissions", "permission_ids", "user_count"]
        read_only_fields = ["id"]

    def get_user_count(self, obj):
        """获取该角色下的用户数量"""
        return obj.user_set.count()


class GroupSimpleSerializer(serializers.ModelSerializer):
    """角色简化序列化器（用于嵌套显示）"""

    class Meta:
        model = Group
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    groups = GroupSimpleSerializer(many=True, read_only=True)
    group_ids = serializers.PrimaryKeyRelatedField(many=True, write_only=True, queryset=Group.objects.all(), source="groups")
    user_permissions = PermissionSimpleSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Permission.objects.all(), source="user_permissions", required=False
    )
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "groups",
            "group_ids",
            "user_permissions",
            "permission_ids",
            "password",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """创建用户"""
        password = validated_data.pop("password", None)
        groups = validated_data.pop("groups", [])
        user_permissions = validated_data.pop("user_permissions", [])

        user = User.objects.create(**validated_data)

        if password:
            user.set_password(password)
            user.save()

        if groups:
            user.groups.set(groups)

        if user_permissions:
            user.user_permissions.set(user_permissions)

        return user

    def update(self, instance, validated_data):
        """更新用户"""
        password = validated_data.pop("password", None)
        groups = validated_data.pop("groups", None)
        user_permissions = validated_data.pop("user_permissions", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        if groups is not None:
            instance.groups.set(groups)

        if user_permissions is not None:
            instance.user_permissions.set(user_permissions)

        instance.save()
        return instance


class UserSimpleSerializer(serializers.ModelSerializer):
    """用户简化序列化器（用于列表显示）"""

    groups = GroupSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "groups",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("新密码两次输入不一致")
        return data
