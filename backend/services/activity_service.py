"""
activity_service.py — 动态业务逻辑

职责：
- 从 DAO 获取 Activities 模型实例后，提取关联数据（如 shop_name）
- 返回序列化后的字典，供路由层直接返回
"""

from typing import Optional
from dao.activity_dao import ActivityDAO


class ActivityService:
    """动态业务逻辑"""

    @staticmethod
    async def list_by_user(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        获取用户动态列表，附带关联店铺名称。

        返回格式：
        {
            "items": [
                {
                    "id": int,
                    "user_id": int,
                    "type": str,
                    "target_id": int,
                    "target_type": str,
                    "content": str | None,
                    "shop_id": int | None,
                    "shop_name": str | None,   # 从 prefetch 的 shop 关系提取
                    "created_at": str,
                },
            ],
            "total": int,
            "page": int,
            "page_size": int,
        }
        """
        result = await ActivityDAO.list_by_user(user_id, page=page, page_size=page_size)
        items = result["items"]
        serialized = []
        for item in items:
            serialized.append({
                "id": item.id,
                "user_id": item.user_id,
                "type": item.type,
                "target_id": item.target_id,
                "target_type": item.target_type,
                "content": item.content,
                "shop_id": item.shop_id,
                "shop_name": item.shop.name if item.shop else None,
                "created_at": item.created_at.isoformat(),
            })
        return {
            "items": serialized,
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
        }
