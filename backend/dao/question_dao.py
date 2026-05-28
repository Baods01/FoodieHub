"""
question_dao.py — 问答区数据访问层

对应 models/interaction.py：ShopQuestions / QuestionAnswers
"""

from typing import Optional, List
from models.interaction import ShopQuestions, QuestionAnswers


class QuestionDAO:
    """问答区 — ShopQuestions + QuestionAnswers"""

    # ==================== ShopQuestions：查询 ====================

    @staticmethod
    async def get_by_id(question_id: int) -> Optional[ShopQuestions]:
        return await ShopQuestions.get_or_none(
            id=question_id, is_active=True
        ).prefetch_related("user")

    @staticmethod
    async def list_by_shop(
        shop_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        qs = ShopQuestions.filter(shop_id=shop_id, is_active=True)
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
        qs = ShopQuestions.filter(user_id=user_id, is_active=True)
        total = await qs.count()
        items = await qs.order_by("-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .prefetch_related("shop") \
            .all()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def count_by_shop(shop_id: int) -> int:
        return await ShopQuestions.filter(shop_id=shop_id, is_active=True).count()

    # ==================== ShopQuestions：写操作 ====================

    @staticmethod
    async def create(
        shop_id: int, user_id: int,
        title: str, content: Optional[str] = None,
    ) -> ShopQuestions:
        return await ShopQuestions.create(
            shop_id=shop_id, user_id=user_id,
            title=title, content=content,
        )

    @staticmethod
    async def update(
        question_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Optional[ShopQuestions]:
        q = await ShopQuestions.get_or_none(id=question_id, is_active=True)
        if not q:
            return None
        if title is not None:
            q.title = title
        if content is not None:
            q.content = content
        await q.save()
        return q

    @staticmethod
    async def delete(question_id: int) -> bool:
        q = await ShopQuestions.get_or_none(id=question_id, is_active=True)
        if not q:
            return False
        q.is_active = False
        await q.save()
        return True

    @staticmethod
    async def increment_like_count(question_id: int) -> None:
        from tortoise.expressions import F
        await ShopQuestions.filter(id=question_id, is_active=True).update(
            like_count=F("like_count") + 1,
        )

    @staticmethod
    async def decrement_like_count(question_id: int) -> None:
        from tortoise.expressions import F
        await ShopQuestions.filter(
            id=question_id, is_active=True, like_count__gt=0,
        ).update(like_count=F("like_count") - 1)

    # ==================== QuestionAnswers：查询 ====================

    @staticmethod
    async def get_answer_by_id(answer_id: int) -> Optional[QuestionAnswers]:
        return await QuestionAnswers.get_or_none(
            id=answer_id, is_active=True
        ).prefetch_related("user", "reply_to_user")

    @staticmethod
    async def list_by_question(question_id: int) -> List[QuestionAnswers]:
        return await QuestionAnswers.filter(
            question_id=question_id, is_active=True,
        ).order_by("created_at") \
         .prefetch_related("user", "reply_to_user") \
         .all()

    # ==================== QuestionAnswers：写操作 ====================

    @staticmethod
    async def create_answer(
        question_id: int, user_id: int, content: str,
        reply_to_user_id: Optional[int] = None,
    ) -> QuestionAnswers:
        return await QuestionAnswers.create(
            question_id=question_id, user_id=user_id,
            content=content, reply_to_user_id=reply_to_user_id,
        )

    @staticmethod
    async def delete_answer(answer_id: int) -> bool:
        a = await QuestionAnswers.get_or_none(id=answer_id, is_active=True)
        if not a:
            return False
        a.is_active = False
        await a.save()
        return True

    # ==================== 级联清理 ====================

    @staticmethod
    async def clear_by_shop(shop_id: int) -> int:
        return await ShopQuestions.filter(
            shop_id=shop_id, is_active=True,
        ).update(is_active=False)

    @staticmethod
    async def clear_by_user(user_id: int) -> int:
        return await ShopQuestions.filter(
            user_id=user_id, is_active=True,
        ).update(is_active=False)
