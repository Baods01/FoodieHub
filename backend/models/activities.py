from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class Activities(BaseModel):
    """
    Activities 表 - 动态表
    """
    id = fields.IntField(pk=True, description="动态唯一标识")
    user_id = fields.IntField(description="产生动态的用户")
    type = fields.CharField(max_length=50, null=False, description="动态类型：rating、comment、question、answer、favorite、add_shop等")
    target_id = fields.IntField(null=False, description="关联目标ID（如评论ID、店铺ID等）")
    target_type = fields.CharField(max_length=50, null=False, description="目标实体类型，便于前端跳转")
    content = fields.CharField(max_length=255, null=True, description='动态摘要，如"评论了店铺XX"')

    class Meta:
        table = "activities"

    def __str__(self):
        return f"Activity {self.id}: {self.type} by User {self.user_id}"