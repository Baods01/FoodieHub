from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .users import Users
from .shops import Shops


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
