from typing import Optional, List

from tortoise.expressions import Q

from models.users import Users
from models.logs import UserBehaviorLogs


class UserDAO:
    """用户数据访问层"""

    @classmethod
    async def create_user(
        cls,
        username: str,
        password: str,
        phone: str,
        email: str,
        **kwargs
    ) -> Users:
        """创建新用户"""
        return await Users.create(
            username=username,
            password=password,
            phone=phone,
            email=email,
            **kwargs
        )

    @classmethod
    async def find_by_id(cls, user_id: int) -> Optional[Users]:
        """根据 ID 查找用户"""
        return await Users.get_or_none(id=user_id, is_active=True)

    @classmethod
    async def find_by_account(cls, account: str) -> Optional[Users]:
        """
        按用户名/手机号/邮箱查找用户（登录用）
        """
        return await Users.get_or_none(
            Q(username=account) | Q(phone=account) | Q(email=account),
            is_active=True
        )

    @classmethod
    async def find_by_username(cls, username: str) -> Optional[Users]:
        """按用户名查找用户"""
        return await Users.get_or_none(username=username, is_active=True)

    @classmethod
    async def find_by_phone(cls, phone: str) -> Optional[Users]:
        """按手机号查找用户"""
        return await Users.get_or_none(phone=phone, is_active=True)

    @classmethod
    async def find_by_email(cls, email: str) -> Optional[Users]:
        """按邮箱查找用户"""
        return await Users.get_or_none(email=email, is_active=True)

    @classmethod
    async def exists(cls, **kwargs) -> bool:
        """检查用户是否存在（支持任意字段）"""
        kwargs.setdefault("is_active", True)
        return await Users.filter(**kwargs).exists()

    @classmethod
    async def check_duplicate(cls, username: str, phone: str, email: str) -> Optional[str]:
        """
        检查用户名、手机号、邮箱是否已存在
        返回已存在的字段名称，如果都不存在则返回 None
        """
        if await cls.exists(username=username):
            return "username"
        if await cls.exists(phone=phone):
            return "phone"
        if await cls.exists(email=email):
            return "email"
        return None

    @classmethod
    async def update_user(cls, user_id: int, **kwargs) -> Optional[Users]:
        """更新用户信息"""
        user = await Users.get_or_none(id=user_id, is_active=True)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            await user.save()
        return user

    @classmethod
    async def delete_user(cls, user_id: int) -> bool:
        """软删除用户"""
        user = await Users.get_or_none(id=user_id, is_active=True)
        if user:
            user.is_active = False
            await user.save()
            return True
        return False

    @classmethod
    async def get_user_stats(cls, user_id: int) -> dict:
        """
        获取用户统计数据
        返回：店铺数、评论数、评分数、收藏数、动态数
        """
        from models.shops import Shops, Comments, Ratings
        from models.users import Activities, Favorites
        from models.logs import UserBehaviorLogs

        # 统计各表数据
        shop_count = await Shops.filter(user_id=user_id, is_active=True).count()
        comment_count = await Comments.filter(user_id=user_id, is_active=True).count()
        rating_count = await Ratings.filter(user_id=user_id, is_active=True).count()
        favorite_count = await Favorites.filter(user_id=user_id, is_active=True).count()
        activity_count = await Activities.filter(user_id=user_id, is_active=True).count()

        return {
            "shop_count": shop_count,
            "comment_count": comment_count,
            "rating_count": rating_count,
            "favorite_count": favorite_count,
            "activity_count": activity_count
        }

    # ============ 用户账户管理 ============
    # NOTE: account_status 字段需要在数据库模型中添加
    # @classmethod
    # async def update_user_account_status(cls, user_id: int, account_status: int) -> Optional[Users]:
    #    """更新用户账户状态（封禁/解封）"""
    #    user = await Users.get_or_none(id=user_id, is_active=True)
    #    if user:
    #        user.account_status = account_status
    #        await user.save()
    #        return user
    #    return None

    @classmethod
    async def create_user_behavior_log(
        cls,
        user_id: int,
        behavior_type: str,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> UserBehaviorLogs:
        """创建用户行为日志"""
        return await UserBehaviorLogs.create(
            user_id=user_id,
            behavior_type=behavior_type,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )

    @classmethod
    async def get_user_behavior_logs(
        cls,
        user_id: int,
        behavior_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[UserBehaviorLogs]:
        """获取用户行为日志列表"""
        query = UserBehaviorLogs.filter(user_id=user_id, is_active=True).order_by("-created_at")
        
        if behavior_type:
            query = query.filter(behavior_type=behavior_type)
            
        return await query.limit(limit).offset(offset).all()

    @classmethod
    async def update_user_avatar(cls, user_id: int, avatar_url: str) -> Optional[Users]:
        """更新用户头像"""
        user = await Users.get_or_none(id=user_id, is_active=True)
        if user:
            user.avatar = avatar_url
            await user.save()
        return user
