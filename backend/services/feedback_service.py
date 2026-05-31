"""
feedback_service.py — 统一反馈工单业务逻辑
"""

from typing import Optional
from dao.feedback_dao import FeedbackDAO
from schemas.feedback import FeedbackCreateRequest, FeedbackResponse
from services.message_service import MessageService


class FeedbackService:
    """反馈工单业务逻辑"""

    @staticmethod
    async def create(user_id: int, req: FeedbackCreateRequest) -> FeedbackResponse:
        obj = await FeedbackDAO.create(
            user_id=user_id,
            type=req.type,
            target_type=req.target_type,
            target_id=req.target_id,
            reason_id=req.reason_id,
            description=req.description,
        )
        return FeedbackResponse(
            id=obj.id, user_id=obj.user_id,
            type=obj.type, target_type=obj.target_type,
            target_id=obj.target_id, reason_id=obj.reason_id,
            description=obj.description, status=obj.status,
            admin_id=None, created_at=obj.created_at,
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
        obj = await FeedbackDAO.approve(feedback_id, admin_id)
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
