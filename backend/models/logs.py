"""
logs.py — 统一操作日志模型

合并原 UserBehaviorLogs 和 AdminOperationLog 为一张 OperationLog 表，
统一记录所有用户（含管理员）的操作行为。

设计原则：
- 日志为追加写入，API 不提供任何删除/修改接口
- 保留 is_active 字段（继承自 BaseModel），仅用于系统内部数据维护
- operator 为外键（支持 Join 查询），operator_name 冗余存储（用户删除后仍可追溯）
"""

from tortoise import fields
from .base import BaseModel


class OperationLog(BaseModel):
    """
    OperationLog 表 — 统一操作日志

    涵盖范围：
    - 普通用户：浏览店铺、评论、点赞、收藏、评分、举报、提交勘误等
    - 管理员：封禁/解封用户或店铺、处理举报、审核勘误、合并店铺、发布公告等
    """
    id = fields.BigIntField(pk=True, description="日志唯一标识")
    operator = fields.ForeignKeyField(
        "models.Users", null=True, related_name="operation_logs",
        on_delete=fields.SET_NULL, description="操作用户（未登录可为空）"
    )
    operator_name = fields.CharField(max_length=50, null=True, description="操作时用户名（冗余，用户删除后保留追溯）")
    action = fields.CharField(max_length=50, null=False, description="操作动作，如 view_shop / comment / ban_user / approve_edit 等")
    target_type = fields.CharField(max_length=50, null=False, description="操作对象类型，如 shop / user / comment / complaint 等")
    target_id = fields.IntField(null=True, description="操作对象ID")
    detail = fields.JSONField(null=True, description="操作详情，如 before/after 快照、封禁原因等")
    ip_address = fields.CharField(max_length=45, null=True, description="客户端IP地址")
    user_agent = fields.TextField(null=True, description="客户端设备信息")
    session_id = fields.CharField(max_length=64, null=True, description="会话ID（未登录用户追踪用）")

    class Meta:
        table = "operation_logs"
        indexes = [
            ("operator_id", "created_at"),
            ("action", "created_at"),
            ("target_type", "target_id"),
        ]

    def __str__(self):
        return f"OpLog {self.id}: {self.action} on {self.target_type} {self.target_id} by {self.operator_name or 'system'}"
