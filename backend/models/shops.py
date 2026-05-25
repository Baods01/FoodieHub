from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


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
    aliases = fields.JSONField(null=True, description="存储别名列表，例如[老店名, 别名]")
    merged_into = fields.ForeignKeyField("models.Shops", null=True, related_name="shops", on_delete=fields.SET_NULL, description="合并后新店铺")
    
    # 新增字段
    price_range = fields.CharField(max_length=50, null=True, description="人均消费价格段，如 30-50 或 50-100")
    business_hours = fields.CharField(max_length=50, null=True, description="营业时间，如 08:00-22:00")
    dining_methods = fields.JSONField(null=True, description="就餐方式：dine_in pickup delivery")
    address_detail = fields.CharField(max_length=200, null=True, description="详细地址")
    tags = fields.JSONField(null=True, description="店铺标签数组")
    
    # 关联表定义
    dict_relations = fields.ReverseRelation["ShopDictRel"]
    comments = fields.ReverseRelation["Comments"]

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
    extra = fields.JSONField(null=True, description="扩展字段，如存储菜品图片URL")

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
        # Unique constraint to ensure one rating per user per shop
        unique_together = [("user_id", "shop_id")]

    def __str__(self):
        return f"Rating {self.id}: User {self.user_id} -> Shop {self.shop_id} ({self.score})"


class Comments(BaseModel):
    """
    Comments 表 - 评论表
    """
    id = fields.BigIntField(pk=True, description="评论唯一标识")
    shop = fields.ForeignKeyField("models.Shops", related_name="comments", on_delete=fields.CASCADE, description="关联的店铺")
    user = fields.ForeignKeyField("models.Users", related_name="comments", on_delete=fields.CASCADE, description="发表评论的用户")
    type = fields.CharField(max_length=20, default="comment", description="评论类型：question 或 comment")
    parent = fields.ForeignKeyField("models.Comments", related_name="replies", null=True, on_delete=fields.CASCADE, description="父评论。NULL表示一级评论；非空表示对该评论的回复")
    root = fields.ForeignKeyField("models.Comments", related_name="descendants", null=True, on_delete=fields.CASCADE, description="根评论（所属的一级评论），用于快速聚合和展示")
    content = fields.TextField(null=False, description="评论内容，支持富文本或纯文本")
    like_count = fields.IntField(default=0, null=False, description="点赞数，冗余字段，便于排序和展示")
    reply_count = fields.IntField(default=0, null=False, description="直接子回复数量，冗余字段，减少 COUNT 查询")
    
    # 关联表定义
    images = fields.ReverseRelation["Images"]  # 评论关联的图片

    class Meta:
        table = "comments"
        indexes = [
            ("shop_id", "root_id", "created_at"),
        ]

    def __str__(self):
        return f"Comment {self.id} on Shop {self.shop_id} by User {self.user_id}"


class CommentsLikes(BaseModel):
    """
    CommentsLikes 表 - 评论点赞表
    """
    id = fields.IntField(pk=True, description="点赞唯一标识")
    user = fields.ForeignKeyField("models.Users", related_name="comments_likes", on_delete=fields.CASCADE, description="点赞用户")
    comment = fields.ForeignKeyField("models.Comments", related_name="likes", on_delete=fields.CASCADE, description="被点赞的评论")
    is_active = fields.BooleanField(default=True, description="是否有效（软删除）")

    class Meta:
        table = "comments_likes"
        # 移除唯一约束，允许多次创建删除（通过 is_active 控制）
        indexes = [
            ("user_id", "comment_id", "created_at"),
        ]

    def __str__(self):
        return f"CommentLike {self.id}: User {self.user_id} -> Comment {self.comment_id}"
