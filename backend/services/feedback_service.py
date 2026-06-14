"""
feedback_service.py — 统一反馈工单业务逻辑

反馈工单（Feedback）是什么？
  用户对平台内容有异议时可以提交反馈工单，包括两种类型：
  1. complaint（举报）：如举报店铺违规、评论不当等
  2. correction（勘误）：如店铺信息有误需要更正

  工单由用户发起，管理员在后台审核处理（通过/驳回）。

调用链路示例（用户提交举报 → 管理员处理）：
  用户端：POST /complaints → FeedbackService.create() → FeedbackDAO.create()
  管理员端：POST /admin/feedbacks/{id}/approve → FeedbackService.approve()
    → FeedbackDAO.approve() → MessageService.create_notification() 通知用户

[教师可能问：为什么叫"feedback"而不是直接用"complaint"？]
  答：因为工单包括"举报"和"勘误"两种类型，feedback 是更通用的命名。
  如果只叫 complaint，后续扩展勘误功能时需要建新的表或改表名。
"""

from typing import Optional
from dao.feedback_dao import FeedbackDAO
from schemas.feedback import FeedbackCreateRequest, FeedbackResponse
from services.message_service import MessageService


class FeedbackService:
    """反馈工单业务逻辑"""

    @staticmethod
    async def create(user_id: int, req: FeedbackCreateRequest) -> FeedbackResponse:
        """
        创建反馈工单。

        参数说明：
          user_id : 提交工单的用户 ID
          req     : FeedbackCreateRequest Pydantic schema，包含类型、目标、原因等

        ★ 执行顺序：
          1. 调用 FeedbackDAO.create() 插入工单记录
             → INSERT INTO feedback (user_id, type, target_type, target_id, reason_id, description, status)
               VALUES (?, ?, ?, ?, ?, ?, 'pending')
             DAO 不校验目标是否存在（由业务规则决定，例如举报一个"已删除的评论"也是允许的）
          2. 手动构造 FeedbackResponse 返回

        返回 FeedbackResponse Pydantic schema（自动序列化）。
        """
        obj = await FeedbackDAO.create(
            user_id=user_id,
            type=req.type,               # "complaint" 或 "correction"
            target_type=req.target_type,  # 被举报对象的类型 "shop"/"comment"/"user"
            target_id=req.target_id,      # 被举报对象的 ID
            reason_id=req.reason_id,      # 举报原因（字典表 ID）
            description=req.description,  # 补充说明
        )
        # ★ 手动构造 FeedbackResponse（因为 DAO 返回的是 Model 实例，不是 Schema）
        # 每个字段都需要手动映射
        return FeedbackResponse(
            id=obj.id, user_id=obj.user_id,
            type=obj.type, target_type=obj.target_type,
            target_id=obj.target_id, reason_id=obj.reason_id,
            description=obj.description, status=obj.status,  # 初始 status="pending"
            admin_id=None,  # 刚创建还没有管理员处理
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    @staticmethod
    async def list(
        type: Optional[str] = None,
        status: Optional[str] = None,
        target_type: Optional[str] = None,
        user_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        管理员后台查看工单列表（支持多维筛选和分页）。

        筛选条件：
        - type="complaint" 只看举报
        - status="pending" 只看待处理
        - user_id=1 只看某用户提交的工单

        返回手动序列化的 dict（因为需要 datetime 转 isoformat）。
        """
        result = await FeedbackDAO.list(
            type=type, status=status,
            target_type=target_type, user_id=user_id,
            page=page, page_size=page_size,
        )
        items = []
        for fb in result["items"]:
            items.append({
                "id": fb.id,
                "user_id": fb.user_id,
                "type": fb.type,
                "target_type": fb.target_type,
                "target_id": fb.target_id,
                "reason_id": fb.reason_id,
                "description": fb.description,
                "status": fb.status,
                "admin_id": fb.admin_id,
                "created_at": fb.created_at.isoformat(),
                "updated_at": fb.updated_at.isoformat(),
            })
        return {
            "items": items,
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
        }

    @staticmethod
    async def approve(feedback_id: int, admin_id: int) -> Optional[FeedbackResponse]:
        """
        管理员通过工单。

        ★ 执行顺序：
          1. FeedbackDAO.approve(feedback_id, admin_id)
             → UPDATE feedback SET status='approved', admin_id=? WHERE id=?
          2. 如果成功，发送系统通知给工单发起人
          3. 返回更新后的 FeedbackResponse

        [教师可能问：通过工单后，具体的"处理动作"在哪里执行？]
          答：当前 approve 只改了工单状态，没有执行具体的"处理动作"。
          例如，如果用户举报了一个违规评论，管理员"通过"举报后，
          评论并没有自动被删除。这是因为：
          - 工单审批和"执行处理"是两步操作
          - 管理员可以在查看工单详情后，手动删除评论
          - 这个设计给了管理员更多的控制权
          如果需要自动化，可以在 approve 后面加一个 callback 机制：
          根据 feedback.target_type 和 feedback.type 自动执行对应的处理逻辑。
        """
        obj = await FeedbackDAO.approve(feedback_id, admin_id)
        if not obj:
            return None
        # ★ 通知发起者（通过 MessageService 发送系统通知）
        type_label = "举报" if obj.type == "complaint" else "勘误"
        desc = obj.description or "(无描述)"
        await MessageService.create_notification(
            recipient_id=obj.user_id,    # 工单发起人
            sender_id=admin_id,           # 处理的管理员
            type="feedback_result",
            title="反馈处理结果",
            content=f"您提交的「{type_label}」已被管理员通过。\n\n反馈内容：{desc}",
            related_entity_type="feedback",
            related_entity_id=obj.id,
        )
        return FeedbackResponse(
            id=obj.id, user_id=obj.user_id,
            type=obj.type, target_type=obj.target_type,
            target_id=obj.target_id, reason_id=obj.reason_id,
            description=obj.description, status=obj.status,
            admin_id=obj.admin_id, created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    @staticmethod
    async def reject(feedback_id: int, admin_id: int) -> Optional[FeedbackResponse]:
        """
        管理员驳回工单。

        逻辑与 approve 对称：
        1. FeedbackDAO.reject() 将状态改为 rejected
        2. 发送通知告知发起人"被驳回"
        """
        obj = await FeedbackDAO.reject(feedback_id, admin_id)
        if not obj:
            return None
        # 通知发起者
        type_label = "举报" if obj.type == "complaint" else "勘误"
        desc = obj.description or "(无描述)"
        await MessageService.create_notification(
            recipient_id=obj.user_id,
            sender_id=admin_id,
            type="feedback_result",
            title="反馈处理结果",
            content=f"您提交的「{type_label}」已被管理员驳回。\n\n反馈内容：{desc}",
            related_entity_type="feedback",
            related_entity_id=obj.id,
        )
        return FeedbackResponse(
            id=obj.id, user_id=obj.user_id,
            type=obj.type, target_type=obj.target_type,
            target_id=obj.target_id, reason_id=obj.reason_id,
            description=obj.description, status=obj.status,
            admin_id=obj.admin_id, created_at=obj.created_at,
            updated_at=obj.updated_at,
        )