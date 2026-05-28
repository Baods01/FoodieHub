"""
complaint_dao.py — 举报数据访问层

对应 models/governance.py：Complaints
与 EditRequestDAO 保持一致的治理工单设计。
"""

from typing import Optional
from models.governance import Complaints
from constants import STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED


class ComplaintDAO:
    """举报表 — Complaints"""

    @staticmethod
    async def get_by_id(complaint_id: int) -> Optional[Complaints]:
        return await Complaints.get_or_none(
            id=complaint_id, is_active=True,
        ).select_related("user", "admin")

    @staticmethod
    async def list(
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        qs = Complaints.filter(is_active=True)
        if status:
            qs = qs.filter(status=status)
        if user_id is not None:
            qs = qs.filter(user_id=user_id)
        total = await qs.count()
        items = await qs.order_by("-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .select_related("user", "admin") \
            .all()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def has_pending_complaint(
        user_id: int, complainant_type: str, complainant_id: int,
    ) -> bool:
        return await Complaints.filter(
            user_id=user_id,
            complainant_type=complainant_type,
            complainant_id=complainant_id,
            status=STATUS_PENDING,
            is_active=True,
        ).exists()

    @staticmethod
    async def get_count_by_status() -> dict:
        """返回各状态的数量统计。"""
        pending = await Complaints.filter(status=STATUS_PENDING, is_active=True).count()
        approved = await Complaints.filter(status=STATUS_APPROVED, is_active=True).count()
        rejected = await Complaints.filter(status=STATUS_REJECTED, is_active=True).count()
        return {
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "total": pending + approved + rejected,
        }

    @staticmethod
    async def create(
        user_id: int,
        complainant_type: str,
        complainant_id: int,
        reason_code: str,
        description: Optional[str] = None,
    ) -> Complaints:
        return await Complaints.create(
            user_id=user_id,
            complainant_type=complainant_type,
            complainant_id=complainant_id,
            reason_code=reason_code,
            description=description,
        )

    @staticmethod
    async def approve(
        complaint_id: int,
        admin_id: int,
        action: str,
        result_description: Optional[str] = None,
    ) -> Optional[Complaints]:
        c = await Complaints.get_or_none(id=complaint_id, is_active=True)
        if not c:
            return None
        c.status = STATUS_APPROVED
        c.admin_id = admin_id
        c.action = action
        if result_description is not None:
            c.result_description = result_description
        await c.save()
        return c

    @staticmethod
    async def reject(
        complaint_id: int,
        admin_id: int,
        result_description: Optional[str] = None,
    ) -> Optional[Complaints]:
        c = await Complaints.get_or_none(id=complaint_id, is_active=True)
        if not c:
            return None
        c.status = STATUS_REJECTED
        c.admin_id = admin_id
        c.action = "dismiss"
        if result_description is not None:
            c.result_description = result_description
        await c.save()
        return c

    @staticmethod
    async def delete(complaint_id: int) -> bool:
        c = await Complaints.get_or_none(id=complaint_id, is_active=True)
        if not c:
            return False
        c.is_active = False
        await c.save()
        return True
