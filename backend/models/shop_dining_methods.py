from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .shops import Shops
from .dining_methods import DiningMethods


class ShopDiningMethods(BaseModel):
    """
    ShopDiningMethods 表 - 店铺与点餐方式的中间表
    """
    id = fields.IntField(pk=True, description="唯一标识")
    shop = fields.ForeignKeyField("models.Shops", related_name="shop_dining_methods", on_delete=fields.CASCADE, description="店铺ID")
    dining_method = fields.ForeignKeyField("models.DiningMethods", related_name="shop_dining_methods", on_delete=fields.CASCADE, description="点餐方式ID")
    sort_order = fields.IntField(default=0, description="用于前端展示顺序")

    class Meta:
        table = "shop_dining_methods"
        # Unique constraint to prevent duplicate associations
        unique_together = [("shop_id", "dining_method_id")]

    def __str__(self):
        return f"ShopDiningMethod {self.id}: Shop {self.shop_id} -> DiningMethod {self.dining_method_id}"