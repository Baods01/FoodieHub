"""
comment_dao.py — 评论区数据访问层

对应 models/interaction.py：ShopComments / CommentReplies
"""

from typing import Optional, List
from models.interaction import ShopComments, CommentReplies


class CommentDAO:
    """评论区 — ShopComments + CommentReplies"""

    # ==================== ShopComments：查询 ====================

    @staticmethod
    async def get_by_id(comment_id: int) -> Optional[ShopComments]:
        return await ShopComments.get_or_none(
            id=comment_id, is_active=True
        ).prefetch_related("user")

    @staticmethod
    async def list_by_shop(
        shop_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        qs = ShopComments.filter(shop_id=shop_id, is_active=True)
        total = await qs.count()
        items = await qs.order_by("-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .prefetch_related("user") \
            .all()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def list_by_user(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        qs = ShopComments.filter(user_id=user_id, is_active=True)
        total = await qs.count()
        items = await qs.order_by("-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .prefetch_related("shop") \
            .all()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def count_by_shop(shop_id: int) -> int:
        return await ShopComments.filter(shop_id=shop_id, is_active=True).count()

    # ==================== ShopComments：写操作 ====================

    @staticmethod
    async def create(shop_id: int, user_id: int, content: str) -> ShopComments:
        return await ShopComments.create(
            shop_id=shop_id, user_id=user_id, content=content,
        )

    @staticmethod
    async def update(comment_id: int, content: str) -> Optional[ShopComments]:
        c = await ShopComments.get_or_none(id=comment_id, is_active=True)
        if not c:
            return None
        c.content = content
        await c.save()
        return c

    @staticmethod
    async def delete(comment_id: int) -> bool:
        c = await ShopComments.get_or_none(id=comment_id, is_active=True)
        if not c:
            return False
        c.is_active = False
        await c.save()
        return True

    @staticmethod
    async def increment_like_count(comment_id: int) -> None:
        from tortoise.expressions import F
        await ShopComments.filter(id=comment_id, is_active=True).update(
            like_count=F("like_count") + 1,
        )

    @staticmethod
    async def decrement_like_count(comment_id: int) -> None:
        from tortoise.expressions import F
        await ShopComments.filter(id=comment_id, is_active=True, like_count__gt=0).update(
            like_count=F("like_count") - 1,
        )

    # ==================== CommentReplies：查询 ====================

    @staticmethod
    async def get_reply_by_id(reply_id: int) -> Optional[CommentReplies]:
        return await CommentReplies.get_or_none(
            id=reply_id, is_active=True
        ).prefetch_related("user", "reply_to_user")

    @staticmethod
    async def list_by_comment(comment_id: int) -> List[CommentReplies]:
        return await CommentReplies.filter(
            comment_id=comment_id, is_active=True,
        ).order_by("created_at") \
         .prefetch_related("user", "reply_to_user") \
         .all()

    # ==================== CommentReplies：写操作 ====================

    @staticmethod
    async def create_reply(
        comment_id: int, user_id: int, content: str,
        reply_to_user_id: Optional[int] = None,
    ) -> CommentReplies:
        return await CommentReplies.create(
            comment_id=comment_id, user_id=user_id,
            content=content, reply_to_user_id=reply_to_user_id,
        )

    @staticmethod
    async def delete_reply(reply_id: int) -> bool:
        r = await CommentReplies.get_or_none(id=reply_id, is_active=True)
        if not r:
            return False
        r.is_active = False
        await r.save()
        return True

    @staticmethod
    async def increment_reply_count(comment_id: int) -> None:
        from tortoise.expressions import F
        await ShopComments.filter(id=comment_id, is_active=True).update(
            reply_count=F("reply_count") + 1,
        )

    @staticmethod
    async def decrement_reply_count(comment_id: int) -> None:
        from tortoise.expressions import F
        await ShopComments.filter(
            id=comment_id, is_active=True, reply_count__gt=0,
        ).update(reply_count=F("reply_count") - 1)

    # ==================== 级联清理 ====================

    @staticmethod
    async def clear_by_shop(shop_id: int) -> int:
        """店铺删除时清理所有一级评论（含级联的回复由外键 CASCADE 处理）。"""
        return await ShopComments.filter(
            shop_id=shop_id, is_active=True,
        ).update(is_active=False)

    @staticmethod
    async def clear_by_user(user_id: int) -> int:
        """用户注销时清理其所有一级评论。"""
        return await ShopComments.filter(
            user_id=user_id, is_active=True,
        ).update(is_active=False)
