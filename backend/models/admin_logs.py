from tortoise import models, fields
from datetime import datetime


class AdminOperationLog(models.Model):
    """
    管理员操作日志模型
    """
    id = fields.BigIntField(pk=True, generated=True)
    operator_id = fields.BigIntField(description="操作人ID")
    operator_account = fields.CharField(max_length=100, description="操作人账号")
    operation_time = fields.DatetimeField(description="操作时间", default=datetime.now)
    operation_ip = fields.CharField(max_length=45, description="操作IP地址")
    operation_type = fields.CharField(max_length=50, description="操作类型")
    operation_module = fields.CharField(max_length=100, description="操作模块")
    target_object_id = fields.BigIntField(null=True, description="操作对象ID")
    target_object_type = fields.CharField(max_length=50, null=True, description="操作对象类型")
    before_snapshot = fields.JSONField(null=True, description="操作前字段快照")
    after_snapshot = fields.JSONField(null=True, description="操作后字段快照")
    operation_result = fields.CharField(max_length=20, default="success", description="操作结果状态")
    operation_description = fields.TextField(null=True, description="操作描述")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "admin_operation_logs"
        indexes = [
            ("operator_id", "operation_time"),
            ("operation_time",),
            ("operation_module",),
            ("target_object_type", "target_object_id"),
        ]

    def __str__(self):
        return f"AdminLog-{self.id}-{self.operator_account}-{self.operation_type}"