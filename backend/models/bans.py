from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class Bans(BaseModel):
    """
    Bans 表 - 封禁记录表
    """
    id = fields.IntField(pk=True, description="封禁记录唯一标识")
    target_type = fields.CharField(max_length=10, null=False, description="封禁对象类型：user 或 shop")
    target_id = fields.IntField(null=False, description="被封禁对象的ID")
    reason = fields.CharField(max_length=255, null=True, description="封禁原因")
    banned_by = fields.ForeignKeyField("models.Users", related_name="banned_records", on_delete=fields.SET_NULL, null=True, description="执行封禁的管理员ID")
    banned_at = fields.DatetimeField(auto_now_add=True, description="封禁时间")
    is_active = fields.BooleanField(default=True, description="是否处于封禁状态：true=封禁中，false=已解封")
    unbanned_at = fields.DatetimeField(null=True, description="解封时间")
    unbanned_by = fields.ForeignKeyField("models.Users", related_name="unbanned_records", on_delete=fields.SET_NULL, null=True, description="执行解封的管理员ID")
    unban_reason = fields.CharField(max_length=255, null=True, description="解封原因")

    class Meta:
        table = "bans"
        indexes = [
            ("target_type", "target_id"),
            ("is_active",),
        ]

    def __str__(self):
        return f"Ban {self.id}: {self.target_type} {self.target_id}"