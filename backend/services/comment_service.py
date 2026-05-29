from typing import Optional, List
from dao.comment_dao import CommentDAO
from dao.like_dao import LikeDAO


class CommentService:
    """评论业务逻辑"""

    @staticmethod
    async def create(shop_id: int, user_id: int, content: str) -> dict:
        c = await CommentDAO.create(shop_id, user_id, content)
        await c.fetch_related("user")
        user = c.user
        return {
            "id": c.id,
            "shop_id": c.shop_id,
            "user": {"id": user.id, "username": user.username, "avatar": user.avatar} if user else None,
            "content": c.content,
            "like_count": 0,
            "reply_count": 0,
            "created_at": c.created_at.isoformat(),
        }

    @staticmethod
    async def list_by_shop(shop_id: int, page: int = 1, page_size: int = 20, user_id: Optional[int] = None) -> dict:
        result = await CommentDAO.list_by_shop(shop_id, page=page, page_size=page_size)
        items = []
        for c in result["items"]:
            user = c.user
            has_liked = False
            if user_id is not None:
                has_liked = await LikeDAO.is_liked(user_id, "shop_comment", c.id)
            items.append({
                "id": c.id,
                "shop_id": c.shop_id,
                "user": {"id": user.id, "username": user.username, "avatar": user.avatar} if user else None,
                "content": c.content,
                "like_count": c.like_count,
                "reply_count": c.reply_count,
                "has_liked": has_liked,
                "created_at": c.created_at.isoformat(),
            })
        return {"items": items, "total": result["total"], "page": result["page"], "page_size": result["page_size"]}

    @staticmethod
    async def list_by_user(user_id: int, page: int = 1, page_size: int = 20) -> dict:
        return await CommentDAO.list_by_user(user_id, page=page, page_size=page_size)

    @staticmethod
    async def update(comment_id: int, content: str) -> Optional[dict]:
        c = await CommentDAO.update(comment_id, content)
        if not c:
            return None
        return {"id": c.id, "content": c.content}

    @staticmethod
    async def delete(comment_id: int) -> bool:
        return await CommentDAO.delete(comment_id)

    @staticmethod
    async def create_reply(comment_id: int, user_id: int, content: str,
                           reply_to_user_id: Optional[int] = None) -> dict:
        await CommentDAO.increment_reply_count(comment_id)
        r = await CommentDAO.create_reply(comment_id, user_id, content, reply_to_user_id)
        await r.fetch_related("user", "reply_to_user")
        user = r.user
        reply_to = r.reply_to_user
        return {
            "id": r.id,
            "comment_id": r.comment_id,
            "user": {"id": user.id, "username": user.username, "avatar": user.avatar} if user else None,
            "content": r.content,
            "reply_to_user": {"id": reply_to.id, "username": reply_to.username} if reply_to else None,
            "like_count": 0,
            "created_at": r.created_at.isoformat(),
        }

    @staticmethod
    async def list_replies(comment_id: int, user_id: Optional[int] = None) -> list:
        result = await CommentDAO.list_by_comment(comment_id)
        items = []
        for r in result:
            user = r.user
            reply_to = r.reply_to_user
            has_liked = False
            if user_id is not None:
                has_liked = await LikeDAO.is_liked(user_id, "comment_reply", r.id)
            items.append({
                "id": r.id,
                "comment_id": r.comment_id,
                "user": {"id": user.id, "username": user.username, "avatar": user.avatar} if user else None,
                "content": r.content,
                "reply_to_user": {"id": reply_to.id, "username": reply_to.username} if reply_to else None,
                "like_count": r.like_count,
                "has_liked": has_liked,
                "created_at": r.created_at.isoformat(),
            })
        return items

    @staticmethod
    async def delete_reply(reply_id: int) -> bool:
        return await CommentDAO.delete_reply(reply_id)

    @staticmethod
    async def toggle_reply_like(user_id: int, reply_id: int) -> dict:
        result = await LikeDAO.toggle(user_id, "comment_reply", reply_id)
        if result["action"] == "liked":
            await CommentDAO.increment_reply_like_count(reply_id)
        elif result["action"] == "unliked":
            await CommentDAO.decrement_reply_like_count(reply_id)
        new_count = await LikeDAO.count_by_entity("comment_reply", reply_id)
        return {"is_liked": result["is_liked"], "like_count": new_count}

    @staticmethod
    async def toggle_like(user_id: int, comment_id: int) -> dict:
        result = await LikeDAO.toggle(user_id, "shop_comment", comment_id)
        if result["action"] == "liked":
            await CommentDAO.increment_like_count(comment_id)
        elif result["action"] == "unliked":
            await CommentDAO.decrement_like_count(comment_id)
        new_count = (await CommentDAO.get_by_id(comment_id)).like_count
        return {"is_liked": result["is_liked"], "like_count": new_count}
