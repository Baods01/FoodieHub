"""
interaction.py — 用户互动模型（评论 + 问答 + 点赞）

设计原则：
- 评论区与问答区各拆分为两张表（一二级分离），不再用 type 字段混用
- 二级回复扁平结构：通过 reply_to_user_id 记录被回复人（仅用于前端 @username 前缀），
  无需 parent_id 自引用，全部回复通过 comment_id / question_id 外键归属一级内容
- 点赞统一通过 ContentLikes 多态表管理，各内容的 like_count 为冗余计数
"""

from tortoise import fields
from .base import BaseModel


# ==============================
#  评论区
# ==============================

class ShopComments(BaseModel):
    """
    ShopComments 表 — 一级评论
    """
    id = fields.BigIntField(pk=True, description="评论唯一标识")
    shop = fields.ForeignKeyField("models.Shops", related_name="shop_comments", on_delete=fields.CASCADE, description="关联店铺")
    user = fields.ForeignKeyField("models.Users", related_name="shop_comments", on_delete=fields.CASCADE, description="发表评论的用户")
    content = fields.TextField(null=False, description="评论内容")
    like_count = fields.IntField(default=0, description="点赞数（冗余字段）")
    reply_count = fields.IntField(default=0, description="二级回复数（冗余字段）")

    class Meta:
        table = "shop_comments"
        indexes = [
            ("shop_id", "created_at"),
        ]

    def __str__(self):
        return f"ShopComment {self.id}: Shop {self.shop_id} by User {self.user_id}"


class CommentReplies(BaseModel):
    """
    CommentReplies 表 — 二级回复

    扁平设计：所有 reply 直接关联到一级评论 (comment_id)，不嵌套。
    reply_to_user 记录被回复人，仅用于前端 @username 显示。
    """
    id = fields.BigIntField(pk=True, description="回复唯一标识")
    comment = fields.ForeignKeyField("models.ShopComments", related_name="replies", on_delete=fields.CASCADE, description="所属一级评论")
    user = fields.ForeignKeyField("models.Users", related_name="comment_replies", on_delete=fields.CASCADE, description="回复用户")
    content = fields.TextField(null=False, description="回复内容")
    reply_to_user = fields.ForeignKeyField(
        "models.Users", null=True, related_name="replied_in_comments",
        on_delete=fields.SET_NULL, description="被回复用户ID（仅用于前端展示 @username 前缀）"
    )
    like_count = fields.IntField(default=0, description="点赞数（冗余字段）")

    class Meta:
        table = "comment_replies"
        indexes = [
            ("comment_id", "created_at"),
        ]

    def __str__(self):
        return f"CommentReply {self.id}: Comment {self.comment_id} by User {self.user_id}"


# ==============================
#  问答区
# ==============================

class ShopQuestions(BaseModel):
    """
    ShopQuestions 表 — 一级问题
    """
    id = fields.BigIntField(pk=True, description="问题唯一标识")
    shop = fields.ForeignKeyField("models.Shops", related_name="shop_questions", on_delete=fields.CASCADE, description="关联店铺")
    user = fields.ForeignKeyField("models.Users", related_name="shop_questions", on_delete=fields.CASCADE, description="提问用户")
    title = fields.CharField(max_length=100, null=False, description="问题概括（短）")
    content = fields.TextField(null=True, description="问题描述（长，可选）")
    like_count = fields.IntField(default=0, description="点赞数（冗余字段）")

    class Meta:
        table = "shop_questions"
        indexes = [
            ("shop_id", "created_at"),
        ]

    def __str__(self):
        return f"ShopQuestion {self.id}: {self.title[:30]}"


class QuestionAnswers(BaseModel):
    """
    QuestionAnswers 表 — 二级回答

    与 CommentReplies 相同的扁平设计：
    - question_id 指向所属一级问题
    - reply_to_user 记录被回复人，仅用于 @username 前缀
    """
    id = fields.BigIntField(pk=True, description="回答唯一标识")
    question = fields.ForeignKeyField("models.ShopQuestions", related_name="answers", on_delete=fields.CASCADE, description="所属一级问题")
    user = fields.ForeignKeyField("models.Users", related_name="question_answers", on_delete=fields.CASCADE, description="回答用户")
    content = fields.TextField(null=False, description="回答内容")
    reply_to_user = fields.ForeignKeyField(
        "models.Users", null=True, related_name="replied_in_questions",
        on_delete=fields.SET_NULL, description="被回复用户ID（仅用于前端展示 @username 前缀）"
    )
    like_count = fields.IntField(default=0, description="点赞数（冗余字段）")

    class Meta:
        table = "question_answers"
        indexes = [
            ("question_id", "created_at"),
        ]

    def __str__(self):
        return f"QuestionAnswer {self.id}: Question {self.question_id} by User {self.user_id}"


# ==============================
#  内容点赞（多态）
# ==============================

class ContentLikes(BaseModel):
    """
    ContentLikes 表 — 内容点赞表（多态关联）

    覆盖 ShopComments / CommentReplies / ShopQuestions / QuestionAnswers
    四种内容的点赞/取消点赞。

    不设唯一约束，点赞切换通过 is_active（继承自 BaseModel）软删除实现：
    - 首次点赞 → insert (is_active=True)
    - 取消点赞 → is_active=False
    - 再次点赞 → is_active=True（复用记录）

    各内容的 like_count 冗余字段在 DAO 层进行更新。
    """
    id = fields.BigIntField(pk=True, description="点赞唯一标识")
    user = fields.ForeignKeyField("models.Users", related_name="content_likes", on_delete=fields.CASCADE, description="点赞用户")
    entity_type = fields.CharField(
        max_length=32, null=False,
        description="被点赞内容类型：shop_comment / comment_reply / shop_question / question_answer"
    )
    entity_id = fields.BigIntField(null=False, description="被点赞内容ID（BigInt 兼容所有互动实体的主键类型）")

    class Meta:
        table = "content_likes"
        indexes = [
            ("entity_type", "entity_id"),                          # 查某条内容的所有点赞
            ("user_id", "entity_type", "entity_id", "created_at"), # 查某用户是否点赞某内容
        ]

    def __str__(self):
        return f"ContentLike {self.id}: {self.entity_type} {self.entity_id} by User {self.user_id}"
