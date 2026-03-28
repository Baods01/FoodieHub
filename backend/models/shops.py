from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .categories import Categories
from .shop_dining_methods import ShopDiningMethods
from .shop_categories import ShopCategories


class Shops(BaseModel):
    """
    Shops 表 - 店铺表
    """
    id = fields.IntField(pk=True, description="店铺唯一标识")
    name = fields.CharField(max_length=100, null=False, description="店铺名称")
    description = fields.TextField(null=True, description="店铺描述")
    is_oncampus = fields.BooleanField(null=True, description="校内校外")
    view_count = fields.IntField(default=0, description="总浏览量（冗余字段）")
    favorite_count = fields.IntField(default=0, description="收藏数（冗余字段）")
    comment_count = fields.IntField(default=0, description="讨论数（冗余字段）")
    average_rating = fields.DecimalField(max_digits=2, decimal_places=1, default=0.0, description="平均评分（冗余字段）")
    # 关联表定义
    shop_dining_methods = fields.ReverseRelation["ShopDiningMethods"]
    shop_categories = fields.ReverseRelation["ShopCategories"]

    class Meta:
        table = "shops"

    def __str__(self):
        return self.name
