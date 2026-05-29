from services.comment_service import CommentService
from services.question_service import QuestionService


class LikeService:
    """统一点赞路由，根据 entity_type 分发到对应的 Service"""

    @staticmethod
    async def toggle(user_id: int, entity_type: str, entity_id: int) -> dict:
        if entity_type == "shop_comment":
            return await CommentService.toggle_like(user_id, entity_id)
        elif entity_type == "comment_reply":
            return await CommentService.toggle_reply_like(user_id, entity_id)
        elif entity_type == "shop_question":
            return await QuestionService.toggle_like(user_id, entity_id)
        elif entity_type == "question_answer":
            return await QuestionService.toggle_answer_like(user_id, entity_id)
        raise ValueError(f"不支持的点赞类型: {entity_type}")
