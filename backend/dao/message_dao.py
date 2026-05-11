from typing import Optional, List
from tortoise.expressions import Q

from models.users import Messages
from models.users import Users


class MessageDAO:
    """消息数据访问层"""

    @classmethod
    async def get_user_messages(
        cls,
        user_id: int,
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[Messages]:
        """获取用户消息列表"""
        query = Messages.filter(
            recipient_id=user_id,
            is_active=True
        ).order_by("-created_at")
        
        if unread_only:
            query = query.filter(is_read=False)
        
        return await query.limit(limit).offset(offset).prefetch_related("sender", "recipient").all()

    @classmethod
    async def get_message_by_id(cls, message_id: int) -> Optional[Messages]:
        """根据ID获取消息"""
        return await Messages.get_or_none(id=message_id, is_active=True).prefetch_related("sender", "recipient")

    @classmethod
    async def mark_message_as_read(cls, message_id: int) -> bool:
        """标记消息为已读"""
        message = await Messages.get_or_none(id=message_id, is_active=True)
        if message:
            message.is_read = True
            await message.save()
            return True
        return False

    @classmethod
    async def mark_all_messages_as_read(cls, user_id: int) -> int:
        """标记用户所有未读消息为已读，返回标记数量"""
        result = await Messages.filter(
            recipient_id=user_id,
            is_active=True,
            is_read=False
        ).update(is_read=True)
        return result

    @classmethod
    async def get_unread_count(cls, user_id: int) -> int:
        """获取用户未读消息数量"""
        return await Messages.filter(
            recipient_id=user_id,
            is_active=True,
            is_read=False
        ).count()

    @classmethod
    async def create_system_message(
        cls,
        title: str,
        content: str,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None
    ) -> Messages:
        """创建系统消息（广播给所有用户）"""
        message = await Messages.create(
            title=title,
            content=content,
            type="announcement",
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        )
        return message

    @classmethod
    async def create_user_message(
        cls,
        recipient_id: int,
        sender_id: Optional[int],
        title: str,
        content: str,
        type: str,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None
    ) -> Messages:
        """创建用户消息"""
        return await Messages.create(
            recipient_id=recipient_id,
            sender_id=sender_id,
            title=title,
            content=content,
            type=type,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        )

    @classmethod
    async def delete_message(cls, message_id: int) -> bool:
        """软删除消息"""
        message = await Messages.get_or_none(id=message_id, is_active=True)
        if message:
            message.is_active = False
            await message.save()
            return True
        return False

    @classmethod
    async def delete_messages_by_user(cls, user_id: int) -> int:
        """软删除用户所有消息，返回删除数量"""
        result = await Messages.filter(recipient_id=user_id, is_active=True).update(is_active=False)
        return result