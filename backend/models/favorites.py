from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .users import Users
from .shops import Shops


class Favorites(BaseModel):
    """
    Favorites 表 - 收藏表
    """
    id = fields.IntField(pk=True, description="收藏唯一标识")
    user = fields.ForeignKeyField("models.Users", related_name="favorites", on_delete=fields.CASCADE, description="收藏用户")
    shop = fields.ForeignKeyField("models.Shops", related_name="favorites", on_delete=fields.CASCADE, description="被收藏店铺")
    sort_order = fields.IntField(default=0, null=False, description="排序序号，数值越小越靠前，用于支持用户手动置顶或自定义顺序")

    class Meta:
        table = "favorites"
        # Unique constraint to prevent duplicate favorites
        unique_together = [("user_id", "shop_id")]

    def __str__(self):
        return f"Favorite {self.id}: User {self.user_id} -> Shop {self.shop_id}"
