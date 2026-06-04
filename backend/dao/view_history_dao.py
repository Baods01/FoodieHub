"""
view_history_dao.py — 浏览历史数据访问层

对应 models/history.py：ViewHistory
"""

from typing import Optional, List
from models.history import ViewHistory


class ViewHistoryDAO:
    """浏览历史表 — ViewHistory"""

    @staticmethod
    async def upsert(user_id: int, shop_id: int) -> ViewHistory:
        """
        记录或更新浏览历史。
        若用户-店铺对已存在，更新 viewed_at；
        否则新建记录。
        """
        record, created = await ViewHistory.get_or_create(
            user_id=user_id, shop_id=shop_id,
            defaults={"is_active": True},
        )
        if not created:
            # auto_now 会自动更新 viewed_at
            await record.save(update_fields=["viewed_at"])
        return record

    @staticmethod
    async def list_by_user(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """用户浏览历史，按浏览时间倒序。"""
        qs = ViewHistory.filter(user_id=user_id, is_active=True)
        total = await qs.count()
        items = await qs.order_by("-viewed_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .select_related("shop") \
            .all()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def delete(view_history_id: int) -> bool:
        """软删除单条历史记录。"""
        record = await ViewHistory.get_or_none(id=view_history_id, is_active=True)
        if not record:
            return False
        record.is_active = False
        await record.save(update_fields=["is_active", "updated_at"])
        return True

    @staticmethod
    async def clear_by_user(user_id: int) -> int:
        """清空用户所有浏览历史。返回清除条数。"""
        count = await ViewHistory.filter(
            user_id=user_id, is_active=True,
        ).update(is_active=False)
        return count
