from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .shops import Shops


class MenuItems(BaseModel):
    """
    Menu_items 表 - 菜单项表
    """
    id = fields.IntField(pk=True, description="菜单项唯一标识")
    shop = fields.ForeignKeyField("models.Shops", related_name="menu_items", on_delete=fields.CASCADE, description="所属店铺")
    name = fields.CharField(max_length=100, null=False, description="菜品名称")
    price = fields.DecimalField(max_digits=10, decimal_places=2, null=True, description="价格")
    description = fields.TextField(null=True, description="菜品描述")

    class Meta:
        table = "menu_items"

    def __str__(self):
        return self.name
