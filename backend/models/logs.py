from tortoise.models import Model
from tortoise import fields
from .base import BaseModel
from .users import Users


class UserBehaviorLogs(BaseModel):
    """
    User_behavior_logs 表 - 用户行为日志表
    """
    id = fields.BigIntField(pk=True, description="日志唯一标识")
    user = fields.ForeignKeyField("models.Users", related_name="behavior_logs", null=True, on_delete=fields.SET_NULL, description="操作用户（未登录用户可为空）")
    session_id = fields.CharField(max_length=64, null=True, description="会话ID，用于追踪未登录用户行为")
    behavior_type = fields.CharField(max_length=32, null=False, description='行为类型，如 view_shop、rate_shop、comment、favorite、share 等')
    target_type = fields.CharField(max_length=32, null=False, description='操作目标类型，如 shop、menu_item、comment、question 等')
    target_id = fields.IntField(null=False, description="目标对象的ID")
    ip_address = fields.CharField(max_length=45, null=True, description="客户端IP地址")
    user_agent = fields.TextField(null=True, description="客户端设备信息")

    class Meta:
        table = "user_behavior_logs"

    def __str__(self):
        return f"Log {self.id}: {self.behavior_type} on {self.target_type} {self.target_id}"