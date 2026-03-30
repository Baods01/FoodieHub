from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .dict_type import ShopDictRel


class Shops(BaseModel):
    """
    Shops 表 - 店铺表
    """
    id = fields.IntField(pk=True, description="店铺唯一标识")
    name = fields.CharField(max_length=100, null=False, description="店铺名称")
    description = fields.TextField(null=True, description="店铺描述")
    view_count = fields.IntField(default=0, description="总浏览量（冗余字段）")
    favorite_count = fields.IntField(default=0, description="收藏数（冗余字段）")
    comment_count = fields.IntField(default=0, description="讨论数（冗余字段）")
    average_rating = fields.DecimalField(max_digits=2, decimal_places=1, default=0.0, description="平均评分（冗余字段）")
    # 关联表定义
    dict_relations = fields.ReverseRelation["ShopDictRel"]

    class Meta:
        table = "shops"

    def __str__(self):
        return self.name
