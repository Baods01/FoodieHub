from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class Comments(BaseModel):
    """
    Comments 表 - 评论表
    """
    id = fields.BigIntField(pk=True, description="评论唯一标识")
    shop_id = fields.IntField(null=False, description="关联的店铺ID（或其它目标实体ID）")
    user_id = fields.IntField(null=False, description="发表评论的用户ID")
    parent_id = fields.BigIntField(null=True, default=None, description="父评论ID。NULL 或 0 表示一级评论；非空表示对该评论的回复")
    root_id = fields.BigIntField(null=True, default=None, description="根评论ID（所属的一级评论ID），用于快速聚合和分页")
    content = fields.TextField(null=False, description="评论内容，支持富文本或纯文本")
    like_count = fields.IntField(default=0, null=False, description="点赞数，冗余字段，便于排序和展示")
    reply_count = fields.IntField(default=0, null=False, description="直接子回复数量，冗余字段，减少 COUNT 查询")

    class Meta:
        table = "comments"

    def __str__(self):
        return f"Comment {self.id} on Shop {self.shop_id} by User {self.user_id}"