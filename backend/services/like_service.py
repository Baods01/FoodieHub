"""
like_service.py — 统一点赞路由分发

这个 Service 的设计模式是"路由分发"（Router Pattern），而不是"业务逻辑"。

为什么需要这个 Service？
  点赞（Like）可以作用于四种内容类型：
  - shop_comment（一级评论）
  - comment_reply（二级回复）
  - shop_question（一级问题）
  - question_answer（二级回答）

  虽然有四种内容类型，但"点赞"这个业务操作的行为是一样的：
  "用户点击点赞按钮 → 切换点赞状态 → 更新 like_count"

  为了避免在 Router 层写一长串 if/elif/else，我们将"根据 entity_type
  分发到不同 Service"的逻辑封装在 LikeService 中。

调用链路：
  POST /likes/toggle（Router 层）
    → LikeService.toggle(entity_type, entity_id)
      → CommentService.toggle_like() 或 QuestionService.toggle_like()
        → LikeDAO.toggle()           ← 操作 ContentLikes 表
        → CommentDAO.increment/decrement_like_count()  ← 更新冗余字段

[教师可能问：为什么不把四种内容的点赞逻辑统一？]
  答：虽然逻辑相似，但更新 like_count 的对象不同：
  - shop_comment → CommentDAO.increment_like_count(comment_id)
  - comment_reply → CommentDAO.increment_reply_like_count(reply_id)
  - shop_question → QuestionDAO.increment_like_count(question_id)
  - question_answer → QuestionDAO.increment_answer_like_count(answer_id)
  每种内容有独立的 DAO 方法，所以分发逻辑是必要的。
  （当然，更好的设计是让 LikeDAO.toggle 直接返回"该加 1 还是减 1"，
   由调用方决定哪个计数器，那就只需要一个统一的方法了。
   其实 current LikeDAO.toggle 已经返回 {"action": "liked"/"unliked"}
   但两个 Service 还是各自写了自己的 toggle_like 逻辑——见注释。）
"""

from services.comment_service import CommentService
from services.question_service import QuestionService


class LikeService:
    """统一点赞路由，根据 entity_type 分发到对应的 Service"""

    @staticmethod
    async def toggle(user_id: int, entity_type: str, entity_id: int) -> dict:
        """
        统一点赞切换入口。

        参数：
          user_id    : 执行点赞的用户
          entity_type: 内容类型（shop_comment / comment_reply / shop_question / question_answer）
          entity_id  : 内容 ID

        返回：{"is_liked": bool, "like_count": int}

        ★ 分发逻辑：
          entity_type 的四个枚举值分别路由到 CommentService 或 QuestionService 的 toggle 方法。
          每个方法内部的逻辑是相同的：
            1. LikeDAO.toggle() → 操作 ContentLikes 表（点赞/取消）
            2. 根据 action 是 liked 还是 unliked，调用对应的 increment/decrement
            3. 返回新状态和新计数
        """
        if entity_type == "shop_comment":
            return await CommentService.toggle_like(user_id, entity_id)
        elif entity_type == "comment_reply":
            return await CommentService.toggle_reply_like(user_id, entity_id)
        elif entity_type == "shop_question":
            return await QuestionService.toggle_like(user_id, entity_id)
        elif entity_type == "question_answer":
            return await QuestionService.toggle_answer_like(user_id, entity_id)
        raise ValueError(f"不支持的点赞类型: {entity_type}")