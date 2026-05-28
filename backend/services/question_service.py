from typing import Optional
from dao.question_dao import QuestionDAO
from dao.like_dao import LikeDAO


class QuestionService:
    """问答业务逻辑"""

    @staticmethod
    async def create(shop_id: int, user_id: int, title: str,
                     content: Optional[str] = None) -> dict:
        q = await QuestionDAO.create(shop_id, user_id, title, content)
        return {"id": q.id, "shop_id": q.shop_id, "title": q.title,
                "content": q.content, "like_count": 0, "created_at": q.created_at}

    @staticmethod
    async def list_by_shop(shop_id: int, page: int = 1, page_size: int = 20) -> dict:
        return await QuestionDAO.list_by_shop(shop_id, page=page, page_size=page_size)

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
        return {"id": a.id, "question_id": a.question_id, "content": a.content,
                "like_count": 0, "created_at": a.created_at}

    @staticmethod
    async def list_answers(question_id: int) -> list:
        return await QuestionDAO.list_by_question(question_id)

    @staticmethod
    async def delete_answer(answer_id: int) -> bool:
        return await QuestionDAO.delete_answer(answer_id)

    @staticmethod
    async def toggle_like(user_id: int, question_id: int) -> dict:
        result = await LikeDAO.toggle(user_id, "shop_question", question_id)
        if result["action"] == "liked":
            await QuestionDAO.increment_like_count(question_id)
        elif result["action"] == "unliked":
            await QuestionDAO.decrement_like_count(question_id)
        new_count = (await QuestionDAO.get_by_id(question_id)).like_count
        return {"is_liked": result["is_liked"], "like_count": new_count}
