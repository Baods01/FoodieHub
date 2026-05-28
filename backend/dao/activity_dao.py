"""
activity_dao.py — 动态数据访问层

对应 models/users.py：Activities
自动生成机制见 services/activity_signals.py（占位，DAO 层开发完成后实现）。
"""

from typing import Optional
from models.users import Activities


class ActivityDAO:
    """动态表 — Activities"""

    @staticmethod
    async def get_by_id(activity_id: int) -> Optional[Activities]:
        return await Activities.get_or_none(id=activity_id, is_active=True)

    @staticmethod
    async def list_by_user(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """用户主页时间线，按时间倒序。"""
        qs = Activities.filter(user_id=user_id, is_active=True)
        total = await qs.count()
        items = await qs.order_by("-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .prefetch_related("shop") \
            .all()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def create(
        user_id: int,
        type: str,
        target_id: int,
        target_type: str,
        content: Optional[str] = None,
        shop_id: Optional[int] = None,
    ) -> Activities:
        return await Activities.create(
            user_id=user_id,
            type=type,
            target_id=target_id,
            target_type=target_type,
            content=content,
            shop_id=shop_id,
        )

    @staticmethod
    async def delete(activity_id: int) -> bool:
        a = await Activities.get_or_none(id=activity_id, is_active=True)
        if not a:
            return False
        a.is_active = False
        await a.save()
        return True

    @staticmethod
    async def clear_by_user(user_id: int) -> int:
        return await Activities.filter(
            user_id=user_id, is_active=True,
        ).update(is_active=False)
