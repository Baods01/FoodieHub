from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class ShopEditRequests(BaseModel):
    """
    Shop_edit_requests 表 - 店铺编辑申请表
    """
    id = fields.IntField(pk=True, description="申请唯一标识")
    shop_id = fields.IntField(description="待修改的店铺")
    user_id = fields.IntField(description="申请用户")
    proposed_data = fields.JSONField(null=False, description="提议修改的字段及新值，JSON格式")
    status = fields.CharField(max_length=20, default="pending", null=False, description="状态：pending、approved、rejected")
    admin_id = fields.IntField(null=True, description="审核管理员")

    class Meta:
        table = "shop_edit_requests"

    def __str__(self):
        return f"Shop Edit Request {self.id}: Shop {self.shop_id}, Status {self.status}"