from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .users import Users
from .shops import Shops


class Comments(BaseModel):
    """
    Comments 表 - 评论表
    """
    id = fields.BigIntField(pk=True, description="评论唯一标识")
    shop = fields.ForeignKeyField("models.Shops", related_name="comments", on_delete=fields.CASCADE, description="关联的店铺")
    user = fields.ForeignKeyField("models.Users", related_name="comments", on_delete=fields.CASCADE, description="发表评论的用户")
    type = fields.CharField(max_length=20, default="comment", description="评论类型：question 或 comment")
    parent = fields.ForeignKeyField("self", related_name="replies", null=True, on_delete=fields.CASCADE, description="父评论。NULL表示一级评论；非空表示对该评论的回复")
    root = fields.ForeignKeyField("self", related_name="descendants", null=True, on_delete=fields.CASCADE, description="根评论（所属的一级评论），用于快速聚合和分页")
    content = fields.TextField(null=False, description="评论内容，支持富文本或纯文本")
    like_count = fields.IntField(default=0, null=False, description="点赞数，冗余字段，便于排序和展示")
    reply_count = fields.IntField(default=0, null=False, description="直接子回复数量，冗余字段，减少 COUNT 查询")
    

    class Meta:
        table = "comments"

    def __str__(self):
        return f"Comment {self.id} on Shop {self.shop_id} by User {self.user_id}"
