from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


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
    category = fields.IntField(description='店铺类别，如"中餐""咖啡"，可能需要关联表')
    dining_methods = fields.IntField(description='点餐方式，如"美团""淘宝"，可能需要关联表')

    class Meta:
        table = "shops"

    def __str__(self):
        return self.name