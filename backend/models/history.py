"""
history.py — 浏览历史模型

独立于 OperationLog（审计日志），专用于用户可见的浏览记录。
每用户-店铺唯一一条，重复浏览自动更新 viewed_at。
"""

from tortoise import fields
from .base import BaseModel


class ViewHistory(BaseModel):
    """
    ViewHistory 表 — 浏览历史

    每用户-店铺对只有一条记录，通过 (user_id, shop_id) 唯一约束保证。
    用户重复访问同一店铺时，viewed_at 自动更新为当前时间。
    """
    user = fields.ForeignKeyField(
        "models.Users", related_name="view_history",
        on_delete=fields.CASCADE, description="浏览用户",
    )
    shop = fields.ForeignKeyField(
        "models.Shops", related_name="view_history",
        on_delete=fields.CASCADE, description="被浏览店铺",
    )
    viewed_at = fields.DatetimeField(
        auto_now=True, description="最近浏览时间",
    )

    class Meta:
        table = "view_history"
        unique_together = (("user_id", "shop_id"),)

    def __str__(self):
        return f"ViewHistory: User {self.user_id} -> Shop {self.shop_id} at {self.viewed_at}"
