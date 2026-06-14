"""
question_service.py — 问答业务逻辑

问答区与评论区的结构对比：
  评论区：
    ShopComments（一级评论）→ Reply（二级回复）
  问答区：
    ShopQuestions（一级问题）→ Answers（二级回答）

  两者的结构是对称的，都是"一二级分离"设计：
  - 二级内容通过 FK 指向一级内容（comment_id / question_id）
  - 二级内容不嵌套（扁平结构），所有回复都在同一层级
  - reply_to_user 字段记录被回复人，仅用于前端 @username 显示

调用链路总览：
  Router → QuestionService.create()
    → QuestionDAO.create() → INSERT INTO shop_questions
    → 手动序列化为 dict
  Router → QuestionService.toggle_like()
    → LikeDAO.toggle() → 操作 ContentLikes 表
    → QuestionDAO.increment/decrement_like_count()

[教师可能问：评论和问答的逻辑非常相似，为什么不用同一个 Service？]
  答：虽然结构相似，但两者的字段和业务逻辑有差异：
  - 一级评论有 content + 图片
  - 一级问题有 title + content（必要时可加图片）
  - 二级回复有 reply_to_user，二级回答也有
  如果合并，会导致大量的 if branch 判断字段差异，反而降低了代码可读性。
  当前拆分为两个 Service，每个约 100 行，维护成本更低。
"""

from typing import Optional, List
from dao.question_dao import QuestionDAO
from dao.like_dao import LikeDAO


class QuestionService:
    """问答业务逻辑"""

    @staticmethod
    async def create(shop_id: int, user_id: int, title: str,
                     content: Optional[str] = None) -> dict:
        """
        创建一级问题。

        ★ 执行顺序：
          1. QuestionDAO.create() → INSERT INTO shop_questions
          2. fetch_related("user") → 预加载 user 关联（用于返回用户信息）
          3. 手动序列化为 dict（不包含图片，因为问题暂不支持图片）

        返回的 dict 结构与 CommentService.create 类似，但多了 title 字段。
        [教师可能问：为什么这里没有同步 shops.comment_count？]
          答：comment_count（讨论数）包括 shop_comments + comment_replies +
          shop_questions + question_answers 四项之和。"提问"会计入讨论数，
          但目前的 sync_comment_count 已经通过原生 SQL 跨表统计了，
          所以不需要在每次提问/回答时显式调用——这是一个定期重算的字段。
          但当评论变化时（create/delete），还是要调用 sync_comment_count。
          这种"关键节点触发重算，其他节点允许短暂不一致"的策略
          在 question 模块中没有显式触发——这是一个疏忽。
        """
        q = await QuestionDAO.create(shop_id, user_id, title, content)
        # ★ fetch_related：从 FK 关联中加载 user 数据
        # 相当于执行一次 SELECT * FROM users WHERE id = q.user_id
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
        """
        获取店铺的问题列表（分页）。

        ★ 执行顺序：
          1. QuestionDAO.list_by_shop() 获取分页数据
             DAO 内部：.prefetch_related("user") + offset/limit
          2. 对每个问题，如果传了 user_id，查询该用户是否已点赞
             ★ 这是 N+1 风险：每页 20 个问题会产生 20 次 is_liked 查询
          3. 手动序列化

        [教师可能问：has_liked 查询为什么在 for 循环中？]
          答：因为需要知道"当前登录用户对每个问题是否已点赞"。
          如果不在循环中查，就需要一次性查出用户对"这批问题"的所有点赞记录，
          然后在内存中做映射。当前实现是简单但低效的。
          改进方案：在循环前执行一次 LikeDAO.get_by_user_and_entities()，
          一次性查出该用户对这批问题的点赞状态。
        """
        result = await QuestionDAO.list_by_shop(shop_id, page=page, page_size=page_size)
        items = []
        for q in result["items"]:
            user = q.user
            has_liked = False
            if user_id is not None:
                # ★ N+1 风险点
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
        """获取某用户提出的所有问题列表。"""
        return await QuestionDAO.list_by_user(user_id, page=page, page_size=page_size)

    @staticmethod
    async def update(question_id: int, title: Optional[str] = None,
                     content: Optional[str] = None) -> Optional[dict]:
        """更新问题标题和内容。"""
        q = await QuestionDAO.update(question_id, title=title, content=content)
        if not q:
            return None
        return {"id": q.id, "title": q.title, "content": q.content}

    @staticmethod
    async def delete(question_id: int) -> bool:
        """
        软删除问题（连带级联处理——由 DAO 做？）。

        [教师可能问：删除问题后，下面的回答怎么办？]
          答：QuestionAnswers 通过 FK question_id 关联到 ShopQuestions，
          on_delete=fields.CASCADE。但因为我们是软删除（is_active=False），
          数据库级的 CASCADE 不会触发。所以回答记录仍然存在，
          但它们关联的问题已被软删除。在查询时，所有被软删除的问题
          都不会出现在结果中，所以回答也变相"不可见"了。
          如果需要同时软删除回答，必须在 DAO 中显式更新：
            await QuestionAnswers.filter(question_id=question_id).update(is_active=False)
          当前没有这样做——这是级联处理的一个缺口。
        """
        return await QuestionDAO.delete(question_id)

    # =============================================================================
    # 二级回答
    # =============================================================================

    @staticmethod
    async def create_answer(question_id: int, user_id: int, content: str,
                            reply_to_user_id: Optional[int] = None) -> dict:
        """
        创建二级回答。

        逻辑与 CommentService.create_reply 完全对称：
        1. QuestionDAO.create_answer() → INSERT INTO question_answers
        2. fetch_related("user", "reply_to_user")
        3. 手动序列化（嵌套 user 和 reply_to_user）
        """
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
        """
        获取某个问题的所有回答列表。

        返回 list（不分页，因为回答数量通常较少）。
        同样有 N+1 的 has_liked 查询问题。
        """
        result = await QuestionDAO.list_by_question(question_id)
        items = []
        for a in result:
            user = a.user
            reply_to = a.reply_to_user
            has_liked = False
            if user_id is not None:
                # ★ N+1 风险点
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
        """软删除回答。"""
        return await QuestionDAO.delete_answer(answer_id)

    # =============================================================================
    # 点赞相关（被 LikeService 路由调用）
    # =============================================================================

    @staticmethod
    async def toggle_answer_like(user_id: int, answer_id: int) -> dict:
        """
        切换对回答的点赞。

        ★ 执行顺序：
          1. LikeDAO.toggle() → 操作 ContentLikes 表
             → 返回 {"action": "liked"/"unliked", "is_liked": bool}
          2. 根据 action 决定：
             - "liked"   → increment_answer_like_count（原子 +1）
             - "unliked" → decrement_answer_like_count（原子 -1，下限 0）
          3. 通过 LikeDAO.count_by_entity() 重新查询最新点赞数
             ★ 这里用 count_by_entity 而不是依赖 increment 的返回值
             是因为增量更新可能由于并发原因不准确，重新 COUNT 更可靠
        """
        result = await LikeDAO.toggle(user_id, "question_answer", answer_id)
        if result["action"] == "liked":
            await QuestionDAO.increment_answer_like_count(answer_id)
        elif result["action"] == "unliked":
            await QuestionDAO.decrement_answer_like_count(answer_id)
        new_count = await LikeDAO.count_by_entity("question_answer", answer_id)
        return {"is_liked": result["is_liked"], "like_count": new_count}

    @staticmethod
    async def toggle_like(user_id: int, question_id: int) -> dict:
        """
        切换对问题的点赞。
        与 toggle_answer_like 逻辑完全一样，只是操作的实体类型不同。
        """
        result = await LikeDAO.toggle(user_id, "shop_question", question_id)
        if result["action"] == "liked":
            await QuestionDAO.increment_like_count(question_id)
        elif result["action"] == "unliked":
            await QuestionDAO.decrement_like_count(question_id)
        # ★ 注意：这里读的是 QuestionDAO.get_by_id 的 like_count 字段（冗余字段）
        # 而不是 LikeDAO.count_by_entity——两种做法混用了
        # 与 toggle_answer_like 的 count_by_entity 不一致——这是个小的代码不一致问题
        new_count = (await QuestionDAO.get_by_id(question_id)).like_count
        return {"is_liked": result["is_liked"], "like_count": new_count}