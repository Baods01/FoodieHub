"""
like_dao.py — 内容点赞数据访问层

对应 models/interaction.py：ContentLikes
多态关联（entity_type + entity_id），覆盖四种互动内容的点赞。
不处理 like_count 同步（Service 层职责），只操作 ContentLikes 表。
"""

from typing import Optional, List
from models.interaction import ContentLikes


class LikeDAO:
    """内容点赞表 — ContentLikes"""

    # ==================== 查 ====================

    @staticmethod
    async def is_liked(user_id: int, entity_type: str, entity_id: int) -> bool:
        """检查用户是否已点赞某内容。"""
        return await ContentLikes.filter(
            user_id=user_id, entity_type=entity_type,
            entity_id=entity_id, is_active=True,
        ).exists()

    @staticmethod
    async def get_by_entity(entity_type: str, entity_id: int) -> List[ContentLikes]:
        """某内容的所有点赞记录。"""
        return await ContentLikes.filter(
            entity_type=entity_type, entity_id=entity_id, is_active=True,
        ).order_by("created_at").all()

    @staticmethod
    async def count_by_entity(entity_type: str, entity_id: int) -> int:
        """某内容的点赞总数。"""
        return await ContentLikes.filter(
            entity_type=entity_type, entity_id=entity_id, is_active=True,
        ).count()

    @staticmethod
    async def get_by_user(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        某用户的所有点赞记录，分页返回。
        返回：{"items": [...], "total": int, "page": int, "page_size": int}
        """
        qs = ContentLikes.filter(user_id=user_id, is_active=True)
        total = await qs.count()
        items = await qs.order_by("-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    # ==================== 写 ====================

    @staticmethod
    async def like(user_id: int, entity_type: str, entity_id: int) -> dict:
        """
        执行点赞。若已存在软删除记录则恢复，否则新建。
        返回 {"action": "liked"} 供 Service 层决策 like_count 的增减。
        """
        existing = await ContentLikes.get_or_none(
            user_id=user_id, entity_type=entity_type, entity_id=entity_id,
        )
        if existing:
            if not existing.is_active:
                existing.is_active = True
                await existing.save()
            return {"action": "liked"}
        await ContentLikes.create(
            user_id=user_id, entity_type=entity_type, entity_id=entity_id,
        )
        return {"action": "liked"}

    @staticmethod
    async def unlike(user_id: int, entity_type: str, entity_id: int) -> dict:
        """
        取消点赞（软删除）。
        返回 {"action": "unliked"} 或 {"action": "none"}（未点赞时）。
        """
        existing = await ContentLikes.get_or_none(
            user_id=user_id, entity_type=entity_type,
            entity_id=entity_id, is_active=True,
        )
        if not existing:
            return {"action": "none"}
        existing.is_active = False
        await existing.save()
        return {"action": "unliked"}

    @staticmethod
    async def toggle(user_id: int, entity_type: str, entity_id: int) -> dict:
        """
        一键切换点赞状态。
        返回 {"action": "liked"|"unliked", "is_liked": bool}
        Service 层根据 action 决定 like_count 是 +1 还是 -1。
        """
        existing = await ContentLikes.get_or_none(
            user_id=user_id, entity_type=entity_type, entity_id=entity_id,
        )
        if existing and existing.is_active:
            existing.is_active = False
            await existing.save()
            return {"action": "unliked", "is_liked": False}
        elif existing and not existing.is_active:
            existing.is_active = True
            await existing.save()
            return {"action": "liked", "is_liked": True}
        else:
            await ContentLikes.create(
                user_id=user_id, entity_type=entity_type, entity_id=entity_id,
            )
            return {"action": "liked", "is_liked": True}

    # ==================== 级联清理 ====================

    @staticmethod
    async def clear_entity_likes(entity_type: str, entity_id: int) -> int:
        """软删除某内容的所有点赞。返回影响记录数。"""
        count = await ContentLikes.filter(
            entity_type=entity_type, entity_id=entity_id, is_active=True,
        ).update(is_active=False)
        return count
