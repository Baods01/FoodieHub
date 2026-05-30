"""
feedback_dao.py — 统一反馈工单数据访问层

对应 models/governance.py：Feedback
"""

from typing import Optional
from models.governance import Feedback


class FeedbackDAO:
    """反馈工单表 — Feedback"""

    @staticmethod
    async def create(
        user_id: int,
        type: str,
        target_type: str,
        target_id: int,
        reason_id: int,
        description: Optional[str] = None,
    ) -> Feedback:
        return await Feedback.create(
            user_id=user_id,
            type=type,
            target_type=target_type,
            target_id=target_id,
            reason_id=reason_id,
            description=description,
        )

    @staticmethod
    async def get_by_id(feedback_id: int) -> Optional[Feedback]:
        return await Feedback.get_or_none(
            id=feedback_id, is_active=True,
        ).select_related("user", "admin", "reason")

    @staticmethod
    async def list(
        type: Optional[str] = None,
        status: Optional[str] = None,
        target_type: Optional[str] = None,
        user_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        qs = Feedback.filter(is_active=True)

        if type:
            qs = qs.filter(type=type)
        if status:
            qs = qs.filter(status=status)
        if target_type:
            qs = qs.filter(target_type=target_type)
        if user_id is not None:
            qs = qs.filter(user_id=user_id)

        total = await qs.count()
        items = await qs.order_by("-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .select_related("user", "admin", "reason") \
            .all()

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def approve(feedback_id: int, admin_id: int) -> Optional[Feedback]:
        fb = await Feedback.get_or_none(id=feedback_id, is_active=True, status="pending")
        if not fb:
            return None
        fb.status = "approved"
        fb.admin_id = admin_id
        await fb.save()
        return fb

    @staticmethod
    async def reject(feedback_id: int, admin_id: int) -> Optional[Feedback]:
        fb = await Feedback.get_or_none(id=feedback_id, is_active=True, status="pending")
        if not fb:
            return None
        fb.status = "rejected"
        fb.admin_id = admin_id
        await fb.save()
        return fb
