from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class Complaints(BaseModel):
    """
    Complaints 表 - 举报投诉表
    """
    id = fields.IntField(pk=True, description="举报唯一标识")
    user = fields.ForeignKeyField("models.Users", related_name="complaints", on_delete=fields.CASCADE, description="举报发起用户")
    complainant_type = fields.CharField(max_length=32, null=False, description="被举报内容类型：comment、shop、image")
    complainant_id = fields.IntField(null=False, description="被举报内容ID")
    reason_code = fields.CharField(max_length=50, null=False, description="举报原因编码，来自字典数据")
    description = fields.TextField(null=True, description="补充说明")
    status = fields.CharField(max_length=20, default="pending", null=False, description="处理状态：pending、approved、rejected")
    
    class Meta:
        table = "complaints"
        indexes = [
            ("complainant_type", "complainant_id"),
            ("status", "created_at"),
        ]

    def __str__(self):
        return f"Complaint {self.id}: {self.complainant_type} {self.complainant_id}"


class ComplaintHandlers(BaseModel):
    """
    ComplaintHandlers 表 - 举报处理记录表
    """
    id = fields.IntField(pk=True, description="处理记录唯一标识")
    complaint = fields.ForeignKeyField("models.Complaints", related_name="handlers", on_delete=fields.CASCADE, description="关联的举报")
    handler = fields.ForeignKeyField("models.Users", related_name="handled_complaints", null=True, on_delete=fields.SET_NULL, description="处理管理员")
    action = fields.CharField(max_length=50, null=False, description="处理动作：delete_comment、ban_shop、remove_image、dismiss等")
    result_description = fields.TextField(null=True, description="处理结果描述")
    
    class Meta:
        table = "complaint_handlers"
        indexes = [
            ("complaint_id", "created_at"),
        ]

    def __str__(self):
        return f"ComplaintHandler {self.id}: Complaint {self.complaint_id} -> Action {self.action}"