"""
history_service.py — 浏览历史业务逻辑

职责：
- 从 ViewHistoryDAO 获取浏览记录后，通过关联的 shop 提取店铺信息
- 返回序列化后的 ViewHistoryItem
"""

from typing import Optional
from dao.view_history_dao import ViewHistoryDAO
from dao.image_dao import ImageDAO


class HistoryService:
    """浏览历史业务逻辑"""

    @staticmethod
    async def get_view_history(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        获取当前用户的店铺浏览历史，附带店铺信息。

        返回格式：
        {
            "items": [
                {
                    "id": int,
                    "shop_id": int,
                    "shop_name": str,
                    "shop_cover": str | None,
                    "region": str | None,
                    "viewed_at": str,
                },
            ],
            "total": int,
            "has_more": bool,
        }
        """
        result = await ViewHistoryDAO.list_by_user(user_id, page=page, page_size=page_size)
        items = result["items"]
        serialized = []
        for item in items:
            shop = getattr(item, "shop", None)
            cover = await ImageDAO.get_first_by_entity("shop", item.shop_id) if shop else None
            serialized.append({
                "id": item.id,
                "shop_id": item.shop_id,
                "shop_name": shop.name if shop else "已删除的店铺",
                "shop_cover": cover.url if cover else None,
                "region": None,
                "viewed_at": item.viewed_at.isoformat(),
            })
        return {
            "items": serialized,
            "total": result["total"],
            "has_more": len(items) + (page - 1) * page_size < result["total"],
        }

    @staticmethod
    async def delete(history_id: int) -> bool:
        """删除单条浏览历史。"""
        return await ViewHistoryDAO.delete(history_id)

    @staticmethod
    async def clear(user_id: int) -> int:
        """清空用户所有浏览历史。"""
        return await ViewHistoryDAO.clear_by_user(user_id)
