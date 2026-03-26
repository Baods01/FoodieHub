from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class Favorites(BaseModel):
    """
    Favorites 表 - 收藏表
    """
    id = fields.IntField(pk=True, description="收藏唯一标识")
    user_id = fields.IntField(description="收藏用户")
    shop_id = fields.IntField(description="被收藏店铺")
    sort_order = fields.IntField(default=0, null=False, description="排序序号，数值越小越靠前，用于支持用户手动置顶或自定义顺序")

    class Meta:
        table = "favorites"
        # Unique constraint to prevent duplicate favorites
        unique_together = [("user_id", "shop_id")]

    def __str__(self):
        return f"Favorite {self.id}: User {self.user_id} -> Shop {self.shop_id}"