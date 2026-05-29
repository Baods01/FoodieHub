from typing import Optional, List
from dao.question_dao import QuestionDAO
from dao.like_dao import LikeDAO


class QuestionService:
    """问答业务逻辑"""

    @staticmethod
    async def create(shop_id: int, user_id: int, title: str,
                     content: Optional[str] = None) -> dict:
        q = await QuestionDAO.create(shop_id, user_id, title, content)
        await q.fetch_related("user")
        user = q.user
        return {
            "id": q.id,
            "shop_id": q.shop_id,
            "user": {"id": user.id, "username": user.username, "avatar": user.avatar} if user else None,
            "title": q.title,
            "content": q.content,
            "like_count": 0,
            "created_at": q.created_at.isoformat(),
        }

    @staticmethod
    async def list_by_shop(shop_id: int, page: int = 1, page_size: int = 20, user_id: Optional[int] = None) -> dict:
        result = await QuestionDAO.list_by_shop(shop_id, page=page, page_size=page_size)
        items = []
        for q in result["items"]:
            user = q.user
            has_liked = False
            if user_id is not None:
                has_liked = await LikeDAO.is_liked(user_id, "shop_question", q.id)
            items.append({
                "id": q.id,
                "shop_id": q.shop_id,
                "user": {"id": user.id, "username": user.username, "avatar": user.avatar} if user else None,
                "title": q.title,
                "content": q.content,
                "like_count": q.like_count,
                "has_liked": has_liked,
                "created_at": q.created_at.isoformat(),
            })
        return {"items": items, "total": result["total"], "page": result["page"], "page_size": result["page_size"]}

    @staticmethod
    async def list_by_user(user_id: int, page: int = 1, page_size: int = 20) -> dict:
        return await QuestionDAO.list_by_user(user_id, page=page, page_size=page_size)

    @staticmethod
    async def update(question_id: int, title: Optional[str] = None,
                     content: Optional[str] = None) -> Optional[dict]:
        q = await QuestionDAO.update(question_id, title=title, content=content)
        if not q:
            return None
        return {"id": q.id, "title": q.title, "content": q.content}

    @staticmethod
    async def delete(question_id: int) -> bool:
        return await QuestionDAO.delete(question_id)

    @staticmethod
    async def create_answer(question_id: int, user_id: int, content: str,
                            reply_to_user_id: Optional[int] = None) -> dict:
        a = await QuestionDAO.create_answer(question_id, user_id, content, reply_to_user_id)
        await a.fetch_related("user", "reply_to_user")
        user = a.user
        reply_to = a.reply_to_user
        return {
            "id": a.id,
            "question_id": a.question_id,
            "user": {"id": user.id, "username": user.username, "avatar": user.avatar} if user else None,
            "content": a.content,
            "reply_to_user": {"id": reply_to.id, "username": reply_to.username} if reply_to else None,
            "like_count": 0,
            "created_at": a.created_at.isoformat(),
        }

    @staticmethod
    async def list_answers(question_id: int, user_id: Optional[int] = None) -> list:
        result = await QuestionDAO.list_by_question(question_id)
        items = []
        for a in result:
            user = a.user
            reply_to = a.reply_to_user
            has_liked = False
            if user_id is not None:
                has_liked = await LikeDAO.is_liked(user_id, "question_answer", a.id)
            items.append({
                "id": a.id,
                "question_id": a.question_id,
                "user": {"id": user.id, "username": user.username, "avatar": user.avatar} if user else None,
                "content": a.content,
                "reply_to_user": {"id": reply_to.id, "username": reply_to.username} if reply_to else None,
                "like_count": a.like_count,
                "has_liked": has_liked,
                "created_at": a.created_at.isoformat(),
            })
        return items

    @staticmethod
    async def delete_answer(answer_id: int) -> bool:
        return await QuestionDAO.delete_answer(answer_id)

    @staticmethod
    async def toggle_answer_like(user_id: int, answer_id: int) -> dict:
        result = await LikeDAO.toggle(user_id, "question_answer", answer_id)
        if result["action"] == "liked":
            await QuestionDAO.increment_answer_like_count(answer_id)
        elif result["action"] == "unliked":
            await QuestionDAO.decrement_answer_like_count(answer_id)
        new_count = await LikeDAO.count_by_entity("question_answer", answer_id)
        return {"is_liked": result["is_liked"], "like_count": new_count}

    @staticmethod
    async def toggle_like(user_id: int, question_id: int) -> dict:
        result = await LikeDAO.toggle(user_id, "shop_question", question_id)
        if result["action"] == "liked":
            await QuestionDAO.increment_like_count(question_id)
        elif result["action"] == "unliked":
            await QuestionDAO.decrement_like_count(question_id)
        new_count = (await QuestionDAO.get_by_id(question_id)).like_count
        return {"is_liked": result["is_liked"], "like_count": new_count}
