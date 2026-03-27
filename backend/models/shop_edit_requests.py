from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .users import Users
from .shops import Shops


class ShopEditRequests(BaseModel):
    """
    Shop_edit_requests 表 - 店铺编辑申请表
    """
    id = fields.IntField(pk=True, description="申请唯一标识")
    shop = fields.ForeignKeyField("models.Shops", related_name="edit_requests", on_delete=fields.CASCADE, description="待修改的店铺")
    user = fields.ForeignKeyField("models.Users", related_name="shop_edit_requests", on_delete=fields.CASCADE, description="申请用户")
    proposed_data = fields.JSONField(null=False, description="提议修改的字段及新值，JSON格式")
    status = fields.CharField(max_length=20, default="pending", null=False, description="状态：pending、approved、rejected")
    admin = fields.ForeignKeyField("models.Users", related_name="handled_edit_requests", null=True, on_delete=fields.SET_NULL, description="审核管理员")

    class Meta:
        table = "shop_edit_requests"

    def __str__(self):
        return f"Shop Edit Request {self.id}: Shop {self.shop_id}, Status {self.status}"
