"""
封禁记录数据访问层
"""
from typing import Optional, Dict, Any
from models.bans import Bans
from models.users import Users
from models.shops import Shops


class BanDAO:
    """封禁记录数据访问对象"""

    @classmethod
    async def create_ban_record(
        cls,
        target_type: str,
        target_id: int,
        reason: Optional[str] = None,
        banned_by: Optional[int] = None
    ) -> Bans:
        """
        创建封禁记录
        """
        return await Bans.create(
            target_type=target_type,
            target_id=target_id,
            reason=reason,
            banned_by_id=banned_by,
            is_active=True
        )

    @classmethod
    async def get_active_ban(cls, target_type: str, target_id: int) -> Optional[Bans]:
        """
        获取指定对象的有效封禁记录
        """
        return await Bans.get_or_none(
            target_type=target_type,
            target_id=target_id,
            is_active=True
        )

    @classmethod
    async def update_ban_record(
        cls,
        ban_id: int,
        **kwargs
    ) -> Optional[Bans]:
        """
        更新封禁记录
        """
        ban = await Bans.get_or_none(id=ban_id)
        if ban:
            for key, value in kwargs.items():
                setattr(ban, key, value)
            await ban.save()
        return ban

    @classmethod
    async def unban(
        cls,
        target_type: str,
        target_id: int,
        unbanned_by: int,
        unban_reason: Optional[str] = None
    ) -> Optional[Bans]:
        """
        执行解封操作
        """
        ban = await cls.get_active_ban(target_type, target_id)
        if ban:
            ban.is_active = False
            ban.unbanned_by_id = unbanned_by
            ban.unban_reason = unban_reason
            from datetime import datetime
            ban.unbanned_at = datetime.now()
            await ban.save()
        return ban

    @classmethod
    async def get_ban_history(cls, target_type: str, target_id: int) -> list:
        """
        获取对象的封禁历史记录
        """
        return await Bans.filter(
            target_type=target_type,
            target_id=target_id
        ).order_by("-created_at").all()

    @classmethod
    async def get_all_bans(
        cls,
        target_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 20
    ) -> dict:
        """
        获取封禁记录列表（支持筛选和分页）
        """
        query = Bans.all().order_by("-created_at")

        if target_type:
            query = query.filter(target_type=target_type)
        if is_active is not None:
            query = query.filter(is_active=is_active)

        total = await query.count()
        offset = (page - 1) * limit
        bans = await query.offset(offset).limit(limit).prefetch_related("banned_by", "unbanned_by").all()

        return {
            "total": total,
            "bans": bans
        }