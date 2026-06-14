"""
message_service.py — 消息通知业务逻辑

消息（Messages）是什么？
  用户在平台上的互动产生通知消息，包括：
  - 有人回复了我的评论 → 消息
  - 有人回答了我的问题 → 消息
  - 有人赞了我的内容 → 消息
  - 管理员发布了公告 → 消息
  - 反馈工单处理完成 → 消息

消息的"生产端"在哪里？
 消息不是由 MessageService 主动"推送"的，而是在 Router/Service 层的业务逻辑末尾
 主动调用 MessageService.create_notification() 生成的。例如：
   - 在 routers/interaction.py 的 create_reply 中，回复别人的评论后调用
   - 在 create_answer 中，回答别人的问题后调用
   - 在 toggle_like 中，点赞后调用
 这种"在业务代码末尾生成通知"的模式叫做"应用层事件"，
 与 activity_signals.py 的"数据库层信号"（post_save）不同。

调用链路示例（回复评论 → 通知评论作者）：
  POST /comments/{comment_id}/replies
    → CommentService.create_reply()
    → MessageService.create_notification(
        recipient_id=comment.user_id,     ← 被回复的人（评论作者）
        sender_id=current_user.id,        ← 回复的人
        type="reply_comment",
        content=f"{current_user.username} 回复了你的评论",
      )
    → MessageDAO.create(...)
      → INSERT INTO messages ...

[教师可能问：为什么不把消息生成逻辑放在 post_save 信号里？]
  答：因为消息的生成需要"业务上下文"——比如需要知道被回复的人的 ID，
  这个 ID 在 CommentReplies 模型的 post_save 信号中可以通过 FK 查询得到，
  但还需要判断"是不是自己回复自己"（不需要通知自己）。
  当前在 Router 层显式调用更可控、逻辑更清晰。
"""

from typing import Optional, List
from dao.message_dao import MessageDAO
from schemas.messages import MessageResponse


class MessageService:
    """消息通知业务逻辑"""

    @staticmethod
    async def list(
        user_id: int,
        unread_only: bool = False,
        type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        获取当前用户的消息列表（支持筛选和分页）。

        参数说明：
          user_id    : 当前用户 ID（必须传，不能查别人的消息）
          unread_only: 只看未读消息
          type       : 按消息类型筛选（如 "reply_comment" 只看回复通知）
          page/page_size: 分页参数

        返回格式：
        {
            "unread_count": int,   # ★ 未读消息总数（独立于分页）
            "items": [...],
            "total": int,
            "page": int,
            "page_size": int,
        }

        ★ 返回结果中的 shop_id 解析逻辑：
          消息本身不直接存储 shop_id，它存的是 related_entity_type 和 related_entity_id。
          为了前端跳转方便，需要在后端将 entity 信息转换为 shop_id。
          例如：
            related_entity_type="comment", related_entity_id=123
            → 查 CommentDAO.get_by_id(123) 拿到 comment.shop_id

          这个转换逻辑就是下面代码中的"反向解析"部分。
          它在 for 循环中对每条消息都执行一次查询——有 N+1 风险。
          但好在消息列表通常只读取最近 20 条，开销不大。

        [教师可能问：为什么不把 shop_id 直接存在 Messages 表中？]
          答：冗余存储可以避免这里的 N+1，但代价是：
          - 插入消息时需要多传一个 shop_id 参数
          - 如果关联的评论/问题被迁移到其他店铺，消息中的 shop_id 就过时了
          当前通过 entity 反向解析，虽然多了一次查询，但数据永远是"最新的"。
        """

        # 第一步：从 DAO 获取原始消息数据
        result = await MessageDAO.list_by_user(
            user_id, unread_only=unread_only, type=type,
            page=page, page_size=page_size,
        )
        items = []
        for msg in result["items"]:
            sender = msg.sender

            # ★ 第二步：反向解析 shop_id（用于前端跳转）
            # 这段逻辑按照 entity 的类型分路径处理
            shop_id = None
            entity_type = msg.related_entity_type
            entity_id = msg.related_entity_id
            if entity_type == "shop":
                # 如果直接关联的是店铺，entity_id 就是 shop_id
                shop_id = entity_id
            elif entity_type in ("comment", "shop_comment"):
                # 如果关联的是评论，需要查评论表拿到 shop_id
                from dao.comment_dao import CommentDAO
                comment = await CommentDAO.get_by_id(entity_id) if entity_id else None
                shop_id = comment.shop_id if comment else None
            elif entity_type in ("question", "question_answer"):
                # 如果关联的是问题或回答，需要反查问题表拿到 shop_id
                from dao.question_dao import QuestionDAO
                if entity_type == "question":
                    question = await QuestionDAO.get_by_id(entity_id) if entity_id else None
                else:
                    # entity_type == "question_answer"：先查回答，再拿问题
                    answer = await QuestionDAO.get_answer_by_id(entity_id) if entity_id else None
                    question = await QuestionDAO.get_by_id(answer.question_id) if answer else None
                shop_id = question.shop_id if question else None

            # 第三步：手动序列化为 dict
            items.append({
                "id": msg.id,
                "type": msg.type,              # 消息类型
                "title": msg.title,            # 标题
                "content": msg.content,        # 内容
                "is_read": msg.is_read,        # 是否已读
                "created_at": msg.created_at.isoformat(),
                "related_entity_type": msg.related_entity_type,
                "related_entity_id": msg.related_entity_id,
                "shop_id": shop_id,            # ★ 反向解析出的 shop_id
                "sender": {
                    "id": sender.id,
                    "username": sender.username,
                    "avatar": sender.avatar,
                } if sender else None,         # 系统消息时 sender 可能为 None
            })
        return {
            "unread_count": result["unread_count"],
            "items": items,
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
        }

    @staticmethod
    async def get_unread_count(user_id: int) -> int:
        """获取用户未读消息总数（用于前端角标显示）。"""
        return await MessageDAO.get_unread_count(user_id)

    @staticmethod
    async def mark_read(user_id: int, message_ids: List[int]) -> int:
        """
        标记指定消息为已读。

        ★ 包含权限校验：只允许标记属于当前用户的消息（msg.recipient_id == user_id）
        防止用户通过 API 调用标记别人的消息（越权操作）。

        [教师可能问：为什么要逐条校验权限？不能用一条 UPDATE 吗？]
          答：可以用 UPDATE messages SET is_read=1 WHERE id IN (...) AND recipient_id=user_id，
          这样数据库层面就做了权限校验，不需要逐条在 Python 中判断。
          当前实现是安全的，但效率不如批量 SQL。改进方案见下。
        """
        marked = 0
        for mid in message_ids:
            msg = await MessageDAO.get_by_id(mid)
            if msg and msg.recipient_id == user_id:
                if await MessageDAO.mark_read(mid):
                    marked += 1
        return marked

    @staticmethod
    async def mark_all_read(user_id: int) -> int:
        """
        标记用户所有消息为已读。

        调用链路：MessageDAO.mark_all_read(user_id)
          → MessageDAO.filter(recipient_id=user_id, is_read=False).update(is_read=True)
            一条 UPDATE SQL 完成，效率高。
        """
        return await MessageDAO.mark_all_read(user_id)

    @staticmethod
    async def delete_messages(user_id: int, message_ids: List[int]) -> int:
        """
        删除指定消息（软删除）。

        同样包含权限校验：只允许删除当前用户收到的消息。
        """
        deleted = 0
        for mid in message_ids:
            msg = await MessageDAO.get_by_id(mid)
            if msg and msg.recipient_id == user_id:
                if await MessageDAO.delete(mid):
                    deleted += 1
        return deleted

    @staticmethod
    async def clear(user_id: int) -> int:
        """清空用户所有消息。"""
        return await MessageDAO.clear_by_user(user_id)

    @staticmethod
    async def send_announcement(title: str, content: str, sender_id: Optional[int] = None) -> int:
        """
        发送系统公告（管理员功能）。

        公告会发送给所有用户，当前实现是逐条 INSERT。
        [教师可能问：用户量大了怎么办？]
          答：如果用户有 10000 人，这里会 INSERT 10000 条记录。
          优化方案：使用"拉模式"——Messages 表中只存公告内容，
          用户未读标记另存一张关联表（user_id, message_id, is_read），
          公告本身存一条，用户登录时再查。
        """
        return await MessageDAO.send_announcement(title, content, sender_id=sender_id)

    @staticmethod
    async def create_notification(
        recipient_id: int,
        sender_id: Optional[int],
        type: str,
        title: str,
        content: str,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None,
    ):
        """
        创建单条通知消息（被 Router 层调用）。

        这是消息系统的"生产端"入口，所有需要在业务操作后通知用户的地方都调用它。

        参数说明：
          recipient_id      : 接收通知的用户 ID（谁该收到这条消息）
          sender_id         : 触发通知的用户 ID（谁做了操作，系统消息时为 None）
          type              : 通知类型，如 "reply_comment"、"like_comment"
          title/content     : 消息标题和内容
          related_entity_*  : 关联实体信息，用于前端点击消息时跳转

        注意：这个方法只是透传调用 MessageDAO.create()，不做任何业务逻辑。
        """
        await MessageDAO.create(
            recipient_id=recipient_id, sender_id=sender_id,
            type=type, title=title, content=content,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )