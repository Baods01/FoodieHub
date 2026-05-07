from typing import Optional

from tortoise.expressions import Q

from models.users import Users


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
        from models.shops import Shops
        from models.comments import Comments
        from models.ratings import Ratings
        from models.favorites import Favorites
        from models.activities import Activities

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
