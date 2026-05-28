"""
governance.py — 平台治理相关模型

包含举报、举报处理、勘误/重复反馈等"用户提交 → 管理员审核"流程的数据模型。
Bans 表已移除（封禁状态通过 Users.is_banned / Shops.is_banned 表达，
封禁/解封历史通过 OperationLog 记录）。
"""

from tortoise import fields
from .base import BaseModel


class Complaints(BaseModel):
    """
    Complaints 表 — 举报投诉表

    与 ShopEditRequests 保持一致的治理工单设计：
    - 用户提交 → admin 审核 → 结果写入本表
    - 处理人（admin）、处理动作（action）、处理备注（result_description）直接内联在举报记录上
    - 不再使用独立的 ComplaintHandlers 表（课程设计场景无需多步骤处理记录）
    """
    id = fields.IntField(pk=True, description="举报唯一标识")
    user = fields.ForeignKeyField("models.Users", related_name="complaints", on_delete=fields.CASCADE, description="举报发起用户")
    complainant_type = fields.CharField(max_length=32, null=False, description="被举报内容类型：comment、shop、image")
    complainant_id = fields.IntField(null=False, description="被举报内容ID")
    reason_code = fields.CharField(max_length=50, null=False, description="举报原因编码，来自字典数据")
    description = fields.TextField(null=True, description="补充说明")
    status = fields.CharField(
        max_length=20, default="pending", null=False,
        description="处理状态：pending=待处理、approved=已通过、rejected=已驳回"
    )
    admin = fields.ForeignKeyField(
        "models.Users", related_name="handled_complaints", null=True,
        on_delete=fields.SET_NULL, description="处理管理员"
    )
    action = fields.CharField(max_length=50, null=True, description="处理动作：delete_comment、ban_shop、remove_image、dismiss 等")
    result_description = fields.TextField(null=True, description="处理结果描述")

    class Meta:
        table = "complaints"
        indexes = [
            ("complainant_type", "complainant_id"),
            ("status", "created_at"),
        ]

    def __str__(self):
        return f"Complaint {self.id}: {self.complainant_type} {self.complainant_id}"


class ShopEditRequests(BaseModel):
    """
    ShopEditRequests 表 — 店铺编辑（勘误/重复）反馈表

    proposed_data 结构：
    - 勘误类型 (type=correction):
        {"type": "correction", "changes": {"name": "...", "area": {"dict_data_id": 9}, "category": {"dict_data_id": 1}}, "reason": "..."}
    - 重复类型 (type=merge):
        {"type": "merge", "candidate_shop_ids": [1, 2, 3], "reason": "..."}
    """
    id = fields.IntField(pk=True, description="申请唯一标识")
    shop = fields.ForeignKeyField("models.Shops", related_name="edit_requests", on_delete=fields.CASCADE, description="待修改的店铺")
    user = fields.ForeignKeyField("models.Users", related_name="shop_edit_requests", on_delete=fields.CASCADE, description="申请用户")
    proposed_data = fields.JSONField(null=False, description="提议修改的字段及新值，JSON格式")
    status = fields.CharField(
        max_length=20, default="pending", null=False,
        description="状态：pending=待处理、approved=已通过、rejected=已驳回"
    )
    admin = fields.ForeignKeyField(
        "models.Users", related_name="handled_edit_requests", null=True,
        on_delete=fields.SET_NULL, description="审核管理员"
    )

    class Meta:
        table = "shop_edit_requests"
        indexes = [
            ("status", "created_at"),
        ]

    def __str__(self):
        return f"ShopEditRequest {self.id}: Shop {self.shop_id}, Status {self.status}"
