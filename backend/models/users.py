from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .shops import Shops


class Users(BaseModel):
    """
    Users 表 - 用户表
    """
    id = fields.IntField(pk=True, description="用户唯一标识")
    username = fields.CharField(max_length=50, unique=True, null=False, description="登录用户名")
    password = fields.CharField(max_length=255, null=False, description="加密后的密码")
    phone = fields.CharField(max_length=20, unique=True, null=False, description="手机号")
    email = fields.CharField(max_length=100, unique=True, null=False, description="电子邮箱，用于通知")
    avatar = fields.CharField(max_length=255, null=True, description="头像图片URL")
    bio = fields.TextField(null=True, description="个人简介")
    role = fields.IntField(default=0, null=False, description="角色：0:user（普通用户）、1:admin（管理员）")

    class Meta:
        table = "users"

    def __str__(self):
        return self.username


class Activities(BaseModel):
    """
    Activities 表 - 动态表
    """
    id = fields.IntField(pk=True, description="动态唯一标识")
    user = fields.ForeignKeyField("models.Users", related_name="activities", on_delete=fields.CASCADE, description="产生动态的用户")
    type = fields.CharField(max_length=50, null=False, description="动态类型：rating、comment、question、answer、favorite、add_shop等")
    target_id = fields.IntField(null=False, description="关联目标ID（如评论ID、店铺ID等）")
    target_type = fields.CharField(max_length=50, null=False, description="目标实体类型，便于前端跳转")
    content = fields.CharField(max_length=255, null=True, description='动态摘要，如"评论了店铺XX"')

    class Meta:
        table = "activities"
        indexes = [
            ("user_id", "created_at"),
        ]

    def __str__(self):
        return f"Activity {self.id}: {self.type} by User {self.user_id}"


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


class Messages(BaseModel):
    """
    Messages 表 - 消息表
    """
    id = fields.IntField(pk=True, description="消息唯一标识")
    recipient = fields.ForeignKeyField("models.Users", related_name="received_messages", on_delete=fields.CASCADE, description="接收用户")
    sender = fields.ForeignKeyField("models.Users", related_name="sent_messages", null=True, on_delete=fields.SET_NULL, description="发送方（系统消息时为空）")
    type = fields.CharField(max_length=50, null=False, description="类型：announcement、reply_comment、reply_answer等")
    title = fields.CharField(max_length=100, null=True, description="消息标题")
    content = fields.TextField(null=False, description="消息内容")
    related_entity_type = fields.CharField(max_length=50, null=True, description="关联实体类型（如comment、answer）")
    related_entity_id = fields.IntField(null=True, description="关联实体ID，用于跳转")

    class Meta:
        table = "messages"
        indexes = [
            ("recipient_id", "created_at"),
        ]

    def __str__(self):
        return f"Message {self.id}: {self.title or 'No Title'}"
