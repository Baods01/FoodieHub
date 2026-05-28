from typing import Optional
from dao.comment_dao import CommentDAO
from dao.like_dao import LikeDAO


class CommentService:
    """评论业务逻辑"""

    @staticmethod
    async def create(shop_id: int, user_id: int, content: str) -> dict:
        c = await CommentDAO.create(shop_id, user_id, content)
        return {"id": c.id, "shop_id": c.shop_id, "content": c.content,
                "like_count": 0, "reply_count": 0, "created_at": c.created_at}

    @staticmethod
    async def list_by_shop(shop_id: int, page: int = 1, page_size: int = 20) -> dict:
        return await CommentDAO.list_by_shop(shop_id, page=page, page_size=page_size)

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
        return {"id": r.id, "comment_id": r.comment_id, "content": r.content,
                "like_count": 0, "created_at": r.created_at}

    @staticmethod
    async def list_replies(comment_id: int) -> list:
        return await CommentDAO.list_by_comment(comment_id)

    @staticmethod
    async def delete_reply(reply_id: int) -> bool:
        return await CommentDAO.delete_reply(reply_id)

    @staticmethod
    async def toggle_like(user_id: int, comment_id: int) -> dict:
        result = await LikeDAO.toggle(user_id, "shop_comment", comment_id)
        if result["action"] == "liked":
            await CommentDAO.increment_like_count(comment_id)
        elif result["action"] == "unliked":
            await CommentDAO.decrement_like_count(comment_id)
        new_count = (await CommentDAO.get_by_id(comment_id)).like_count
        return {"is_liked": result["is_liked"], "like_count": new_count}
