from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .users import Users


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

    def __str__(self):
        return f"Message {self.id}: {self.title or 'No Title'}"
