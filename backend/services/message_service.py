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
        result = await MessageDAO.list_by_user(
            user_id, unread_only=unread_only, type=type,
            page=page, page_size=page_size,
        )
        items = []
        for msg in result["items"]:
            sender = msg.sender
            items.append({
                "id": msg.id,
                "type": msg.type,
                "title": msg.title,
                "content": msg.content,
                "is_read": msg.is_read,
                "created_at": msg.created_at.isoformat(),
                "related_entity_type": msg.related_entity_type,
                "related_entity_id": msg.related_entity_id,
                "sender": {
                    "id": sender.id,
                    "username": sender.username,
                    "avatar": sender.avatar,
                } if sender else None,
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
        return await MessageDAO.get_unread_count(user_id)

    @staticmethod
    async def mark_read(user_id: int, message_ids: List[int]) -> int:
        marked = 0
        for mid in message_ids:
            msg = await MessageDAO.get_by_id(mid)
            if msg and msg.recipient_id == user_id:
                if await MessageDAO.mark_read(mid):
                    marked += 1
        return marked

    @staticmethod
    async def mark_all_read(user_id: int) -> int:
        return await MessageDAO.mark_all_read(user_id)

    @staticmethod
    async def delete_messages(user_id: int, message_ids: List[int]) -> int:
        deleted = 0
        for mid in message_ids:
            msg = await MessageDAO.get_by_id(mid)
            if msg and msg.recipient_id == user_id:
                if await MessageDAO.delete(mid):
                    deleted += 1
        return deleted

    @staticmethod
    async def clear(user_id: int) -> int:
        return await MessageDAO.clear_by_user(user_id)

    @staticmethod
    async def send_announcement(title: str, content: str, sender_id: Optional[int] = None) -> int:
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
        await MessageDAO.create(
            recipient_id=recipient_id, sender_id=sender_id,
            type=type, title=title, content=content,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )
