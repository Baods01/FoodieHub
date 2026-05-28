"""
edit_request_dao.py — 店铺编辑（勘误/重复）反馈数据访问层

对应 models/governance.py：ShopEditRequests
与 ComplaintDAO 保持一致的治理工单设计。
"""

from typing import Optional
from models.governance import ShopEditRequests
from constants import STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED


class EditRequestDAO:
    """店铺编辑反馈表 — ShopEditRequests"""

    @staticmethod
    async def get_by_id(request_id: int) -> Optional[ShopEditRequests]:
        return await ShopEditRequests.get_or_none(
            id=request_id, is_active=True,
        ).select_related("shop", "user", "admin")

    @staticmethod
    async def list(
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        shop_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        qs = ShopEditRequests.filter(is_active=True)
        if status:
            qs = qs.filter(status=status)
        if user_id is not None:
            qs = qs.filter(user_id=user_id)
        if shop_id is not None:
            qs = qs.filter(shop_id=shop_id)
        total = await qs.count()
        items = await qs.order_by("-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .select_related("shop", "user", "admin") \
            .all()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def create(
        shop_id: int,
        user_id: int,
        proposed_data: dict,
    ) -> ShopEditRequests:
        return await ShopEditRequests.create(
            shop_id=shop_id, user_id=user_id, proposed_data=proposed_data,
        )

    @staticmethod
    async def approve(
        request_id: int,
        admin_id: int,
    ) -> Optional[ShopEditRequests]:
        r = await ShopEditRequests.get_or_none(id=request_id, is_active=True)
        if not r:
            return None
        r.status = STATUS_APPROVED
        r.admin_id = admin_id
        await r.save()
        return r

    @staticmethod
    async def reject(
        request_id: int,
        admin_id: int,
    ) -> Optional[ShopEditRequests]:
        r = await ShopEditRequests.get_or_none(id=request_id, is_active=True)
        if not r:
            return None
        r.status = STATUS_REJECTED
        r.admin_id = admin_id
        await r.save()
        return r

    @staticmethod
    async def delete(request_id: int) -> bool:
        r = await ShopEditRequests.get_or_none(id=request_id, is_active=True)
        if not r:
            return False
        r.is_active = False
        await r.save()
        return True
