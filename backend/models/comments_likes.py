from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .users import Users
from .comments import Comments


class CommentsLikes(BaseModel):
    """
    CommentsLikes 表 - 评论点赞表
    """
    id = fields.IntField(pk=True, description="点赞唯一标识")
    user = fields.ForeignKeyField("models.Users", related_name="comments_likes", on_delete=fields.CASCADE, description="点赞用户")
    comment = fields.ForeignKeyField("models.Comments", related_name="likes", on_delete=fields.CASCADE, description="被点赞的评论")

    class Meta:
        table = "comments_likes"
        # 唯一性约束
        unique_together = [("user_id", "comment_id")]

    def __str__(self):
        return f"CommentLike {self.id}: User {self.user_id} -> Comment {self.comment_id}"