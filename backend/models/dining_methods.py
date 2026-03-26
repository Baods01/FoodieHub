from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class DiningMethods(BaseModel):
    """
    Dining_methods 表 - 点餐方式表
    """
    id = fields.IntField(pk=True, description="唯一标识")
    name = fields.CharField(max_length=50, unique=True, null=False, description='点餐方式名称，如"堂食""外卖""自取"')
    description = fields.CharField(max_length=255, null=True, description='描述，如"在店内就餐"')
    sort_order = fields.IntField(default=0, description="排序顺序，用于前端展示顺序")

    class Meta:
        table = "dining_methods"

    def __str__(self):
        return self.name