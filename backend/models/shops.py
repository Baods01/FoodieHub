from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class Shops(BaseModel):
    """
    Shops 表 - 店铺表

    核心字段仅保留名称，其余标签属性（品类、区域、就餐方式等）
    统一通过 DictData + ShopDictRel 字典体系管理。
    描述、人均价格、营业时间等易主观/过时的字段已移除。
    """
    id = fields.IntField(pk=True, description="店铺唯一标识")
    name = fields.CharField(max_length=100, null=False, description="店铺名称（全平台唯一）")
    view_count = fields.IntField(default=0, description="总浏览量（冗余字段）")
    favorite_count = fields.IntField(default=0, description="收藏数（冗余字段）")
    comment_count = fields.IntField(default=0, description="讨论数（冗余字段）")
    average_rating = fields.FloatField(default=0.0, description="平均评分（冗余字段）")
    aliases = fields.JSONField(null=True, description="存储别名列表，例如[老店名, 别名]，支持多名称搜索")
    merged_into = fields.ForeignKeyField(
        "models.Shops", null=True, related_name="shops",
        on_delete=fields.SET_NULL, description="合并后目标店铺ID"
    )
    is_banned = fields.BooleanField(default=False, description="是否被封禁：true=封禁中，false=正常")

    # 关联表定义
    dict_relations = fields.ReverseRelation["ShopDictRel"]

    class Meta:
        table = "shops"

    def __str__(self):
        return self.name


class Menu(BaseModel):
    """
    Menu 表 - 菜单项表

    菜品图片统一通过 Images 表（entity_type='menu_item'）管理。
    """
    id = fields.IntField(pk=True, description="菜单项唯一标识")
    shop = fields.ForeignKeyField("models.Shops", related_name="menu_items", on_delete=fields.CASCADE, description="所属店铺")
    name = fields.CharField(max_length=100, null=False, description="菜品名称")
    price = fields.FloatField(null=True, description="价格")
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
    score = fields.IntField(description="评分值（1-5）")

    class Meta:
        table = "ratings"
        unique_together = [("user_id", "shop_id")]

    def __str__(self):
        return f"Rating {self.id}: User {self.user_id} -> Shop {self.shop_id} ({self.score})"
