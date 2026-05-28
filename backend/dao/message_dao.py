"""
message_dao.py — 消息通知数据访问层

对应 models/users.py：Messages
"""

from typing import Optional, List
from models.users import Messages, Users


class MessageDAO:
    """消息表 — Messages"""

    # ==================== 查询 ====================

    @staticmethod
    async def get_by_id(message_id: int) -> Optional[Messages]:
        return await Messages.get_or_none(
            id=message_id, is_active=True
        ).prefetch_related("sender", "recipient")

    @staticmethod
    async def list_by_user(
        user_id: int,
        unread_only: bool = False,
        type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        用户消息列表，按时间倒序。附带未读数方便 badge 展示。
        返回：{"items": [...], "total": int, "page": int, "page_size": int, "unread_count": int}
        """
        qs = Messages.filter(recipient_id=user_id, is_active=True)

        if unread_only:
            qs = qs.filter(is_read=False)
        if type:
            qs = qs.filter(type=type)

        total = await qs.count()
        items = await qs.order_by("-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .prefetch_related("sender", "recipient") \
            .all()
        unread_count = await Messages.filter(
            recipient_id=user_id, is_active=True, is_read=False,
        ).count()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "unread_count": unread_count,
        }

    @staticmethod
    async def count_by_user(user_id: int,
                            type: Optional[str] = None) -> int:
        qs = Messages.filter(recipient_id=user_id, is_active=True)
        if type:
            qs = qs.filter(type=type)
        return await qs.count()

    @staticmethod
    async def get_unread_count(user_id: int) -> int:
        return await Messages.filter(
            recipient_id=user_id, is_active=True, is_read=False,
        ).count()

    # ==================== 读操作（状态变更） ====================

    @staticmethod
    async def mark_read(message_id: int) -> bool:
        msg = await Messages.get_or_none(id=message_id, is_active=True)
        if not msg:
            return False
        msg.is_read = True
        await msg.save()
        return True

    @staticmethod
    async def mark_all_read(user_id: int) -> int:
        """标记全部未读为已读，返回标记数。"""
        return await Messages.filter(
            recipient_id=user_id, is_active=True, is_read=False,
        ).update(is_read=True)

    # ==================== 写操作 ====================

    @staticmethod
    async def create(
        recipient_id: int,
        sender_id: Optional[int],
        type: str,
        title: str,
        content: str,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None,
    ) -> Messages:
        return await Messages.create(
            recipient_id=recipient_id,
            sender_id=sender_id,
            type=type,
            title=title,
            content=content,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )

    @staticmethod
    async def send_announcement(
        title: str,
        content: str,
        sender_id: Optional[int] = None,
    ) -> int:
        """
        系统公告：发给所有活跃用户，逐条插入。
        返回发送条数。
        """
        active_users = await Users.filter(is_active=True).only("id")
        for user in active_users:
            await Messages.create(
                recipient_id=user.id,
                sender_id=sender_id,
                title=title,
                content=content,
                type="announcement",
            )
        return len(active_users)

    # ==================== 删除 ====================

    @staticmethod
    async def delete(message_id: int) -> bool:
        msg = await Messages.get_or_none(id=message_id, is_active=True)
        if not msg:
            return False
        msg.is_active = False
        await msg.save()
        return True

    @staticmethod
    async def clear_by_user(user_id: int) -> int:
        """清空用户所有消息，返回清除数。"""
        return await Messages.filter(
            recipient_id=user_id, is_active=True,
        ).update(is_active=False)
