from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class Users(BaseModel):
    """
    Users 表 - 用户表
    """
    id = fields.IntField(pk=True, description="用户唯一标识")
    username = fields.CharField(max_length=50, unique=True, null=False, description="登录用户名")
    password = fields.CharField(max_length=255, null=False, description="加密后的密码")
    phone = fields.CharField(max_length=20, null=False, description="手机号")
    email = fields.CharField(max_length=100, null=False, description="电子邮箱，用于通知")
    avatar = fields.CharField(max_length=255, null=True, description="头像图片URL")
    bio = fields.TextField(null=True, description="个人简介")
    role = fields.IntField(default=0, null=False, description="角色：0:user（普通用户）、1:admin（管理员）")

    class Meta:
        table = "users"

    def __str__(self):
        return self.username