"""
governance.py — 平台治理模型

统一 Feedback 表，合并举报与勘误。
"""

from tortoise import fields
from .base import BaseModel


class Feedback(BaseModel):
    """
    Feedback 表 — 统一反馈工单

    合并旧 Complaints 与 ShopEditRequests 两张表。
    type 字段区分举报 (complaint) 与勘误 (edit_request)，
    审核流程统一：提交 → 管理员处理 → 通过/驳回。
    """
    id = fields.IntField(pk=True, description="反馈唯一标识")

    # 提交人
    user = fields.ForeignKeyField(
        "models.Users", related_name="feedbacks",
        on_delete=fields.CASCADE, description="提交用户",
    )

    # 反馈类型
    type = fields.CharField(
        max_length=20, null=False,
        description="complaint=举报 | edit_request=勘误",
    )

    # 反馈对象（多态）
    target_type = fields.CharField(
        max_length=20, null=False,
        description="反馈对象类型：shop / comment / image",
    )
    target_id = fields.IntField(null=False, description="被反馈对象ID")

    # 原因（FK → DictData，前端可选值由 /dict/data?type_name=反馈原因 提供）
    reason = fields.ForeignKeyField(
        "models.DictData", null=False, description="反馈原因",
    )

    # 用户补充说明
    description = fields.TextField(null=True, description="用户填写的补充描述")

    # 审核
    status = fields.CharField(
        max_length=20, default="pending", null=False,
        description="pending=待处理 | approved=已采纳 | rejected=已驳回",
    )
    admin = fields.ForeignKeyField(
        "models.Users", null=True, related_name="handled_feedbacks",
        on_delete=fields.SET_NULL, description="处理管理员",
    )

    class Meta:
        table = "feedbacks"
        indexes = [
            ("status", "created_at"),
            ("target_type", "target_id"),
        ]

    def __str__(self):
        return f"Feedback {self.id}: {self.type} on {self.target_type} {self.target_id} by User {self.user_id}"
