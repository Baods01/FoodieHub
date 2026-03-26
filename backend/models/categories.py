from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class Categories(BaseModel):
    """
    Categories 表 - 类别表
    """
    id = fields.IntField(pk=True, description="类别唯一标识")
    name = fields.CharField(max_length=50, unique=True, null=False, description='类别名称，如"中餐""咖啡"')
    description = fields.CharField(max_length=255, null=True, description="类别描述")
    sort_order = fields.IntField(default=0, description="排序顺序")

    class Meta:
        table = "categories"

    def __str__(self):
        return self.name