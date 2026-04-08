from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .dict import ShopDictRel
from .users import Users


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


class Menu(BaseModel):
    """
    Menu 表 - 菜单项表（原 MenuItems）
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


class Ratings(BaseModel):
    """
    Ratings 表 - 评分表
    """
    id = fields.IntField(pk=True, description="评分唯一标识")
    user = fields.ForeignKeyField("models.Users", related_name="ratings", on_delete=fields.CASCADE, description="评分用户")
    shop = fields.ForeignKeyField("models.Shops", related_name="ratings", on_delete=fields.CASCADE, description="被评店铺")
    score = fields.IntField(description="评分值")  # Note: In MySQL, we'll use a constraint to ensure 1-5 range

    class Meta:
        table = "ratings"
        # Unique constraint to ensure one rating per user per shop
        unique_together = [("user_id", "shop_id")]

    def __str__(self):
        return f"Rating {self.id}: User {self.user_id} -> Shop {self.shop_id} ({self.score})"