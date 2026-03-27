from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .shops import Shops
from .categories import Categories


class ShopCategories(BaseModel):
    """
    ShopCategories 表 - 店铺与类别的中间表
    """
    id = fields.IntField(pk=True, description="唯一标识")
    shop = fields.ForeignKeyField("models.Shops", related_name="shop_categories", on_delete=fields.CASCADE, description="店铺ID")
    category = fields.ForeignKeyField("models.Categories", related_name="shop_categories", on_delete=fields.CASCADE, description="类别ID")

    class Meta:
        table = "shop_categories"
        # Unique constraint to prevent duplicate associations
        unique_together = [("shop_id", "category_id")]

    def __str__(self):
        return f"ShopCategory {self.id}: Shop {self.shop_id} -> Category {self.category_id}"