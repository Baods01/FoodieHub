"""
history_service.py — 浏览历史业务逻辑

职责：
- 从 LogDAO 获取浏览日志记录后，通过 ShopsDAO 补充店铺信息
- 返回序列化后的 ViewHistoryItem，供路由层直接返回
"""

from typing import Optional
from dao.log_dao import LogDAO
from dao.shops_dao import ShopsDAO


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
        result = await LogDAO.get_user_view_logs(
            user_id, action="view_shop", page=page, page_size=page_size,
        )
        items = result["items"]
        serialized = []
        for item in items:
            # 用 target_id 查店铺信息
            shop = await ShopsDAO.get_by_id(item.target_id) if item.target_id else None
            serialized.append({
                "id": item.id,
                "shop_id": item.target_id,
                "shop_name": shop.name if shop else "已删除的店铺",
                "shop_cover": shop.cover_image if shop else None,
                "region": None,  # dict_data 关联在 ShopDAO 中未直接返回，暂空
                "viewed_at": item.created_at.isoformat(),
            })
        return {
            "items": serialized,
            "total": result["total"],
            "has_more": len(items) + (page - 1) * page_size < result["total"],
        }
