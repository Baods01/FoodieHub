"""
user_dao.py — 用户数据访问层

仅处理 Users 表。
其他关联数据（评论、收藏、问答、统计）已移出，见下方 TODO 列表。
"""

from typing import Optional, List
from tortoise.expressions import Q
from models.users import Users


class UserDAO:
    """用户表 — Users"""

    # ==================== 单条查询 ====================

    @staticmethod
    async def get_by_id(user_id: int) -> Optional[Users]:
        return await Users.get_or_none(id=user_id, is_active=True)

    @staticmethod
    async def get_by_username(username: str) -> Optional[Users]:
        return await Users.get_or_none(username=username, is_active=True)

    @staticmethod
    async def get_by_phone(phone: str) -> Optional[Users]:
        return await Users.get_or_none(phone=phone, is_active=True)

    @staticmethod
    async def get_by_email(email: str) -> Optional[Users]:
        return await Users.get_or_none(email=email, is_active=True)

    @staticmethod
    async def get_by_account(account: str) -> Optional[Users]:
        """
        登录用：按用户名/手机号/邮箱匹配，仅查正常用户（is_active=True）。
        如果用户被封禁，此处返回 None，提示"账号或密码错误"（不暴露封禁信息给未登录者）。
        """
        return await Users.get_or_none(
            Q(username=account) | Q(phone=account) | Q(email=account),
            is_active=True,
        )

    @staticmethod
    async def get_by_account_include_banned(account: str) -> Optional[Users]:
        """
        登录用（含封禁用户）：按用户名/手机号/邮箱匹配，查全部状态。
        用于区分"账号不存在"和"账号被封禁"，在 Service 层给出不同提示。
        """
        return await Users.filter(
            Q(username=account) | Q(phone=account) | Q(email=account),
        ).first()

    # ==================== 列表 ====================

    @staticmethod
    async def list(
        is_active: Optional[bool] = None,
        is_banned: Optional[bool] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        管理员后台：用户列表，分页 + 筛选 + 搜索。
        返回：{"items": [...], "total": int, "page": int, "page_size": int}
        """
        qs = Users.all()

        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if is_banned is not None:
            qs = qs.filter(is_banned=is_banned)
        if keyword:
            qs = qs.filter(
                Q(username__icontains=keyword)
                | Q(phone__icontains=keyword)
                | Q(email__icontains=keyword)
            )

        total = await qs.count()
        items = await qs.order_by("-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    # ==================== 写操作 ====================

    @staticmethod
    async def exists(**kwargs) -> bool:
        """检查用户是否存在。"""
        return await Users.filter(**kwargs).exists()

    @staticmethod
    async def check_duplicate(username: str, phone: str, email: str) -> Optional[str]:
        """
        注册查重：若用户名/手机号/邮箱已存在，返回对应的字段名。
        都不存在返回 None。
        """
        if await Users.filter(username=username, is_active=True).exists():
            return "username"
        if await Users.filter(phone=phone, is_active=True).exists():
            return "phone"
        if await Users.filter(email=email, is_active=True).exists():
            return "email"
        return None

    @staticmethod
    async def create(
        username: str,
        password: str,
        phone: str,
        email: str,
        **kwargs,
    ) -> Users:
        return await Users.create(
            username=username,
            password=password,
            phone=phone,
            email=email,
            **kwargs,
        )

    @staticmethod
    async def update(user_id: int, **kwargs) -> Optional[Users]:
        """更新用户信息（含头像）。"""
        user = await Users.get_or_none(id=user_id, is_active=True)
        if not user:
            return None
        for k, v in kwargs.items():
            setattr(user, k, v)
        await user.save()
        return user

    @staticmethod
    async def delete(user_id: int) -> bool:
        """软删除用户（注销账号）。"""
        user = await Users.get_or_none(id=user_id, is_active=True)
        if not user:
            return False
        user.is_active = False
        await user.save()
        return True


# ===========================================================================
# TODO — 以下方法已从 UserDAO 移出，请在对应文件实现后取消注释并删掉此提示：
#
#   方法                                → 目标 DAO 文件
#   get_user_comments()                 → comment_dao.py
#   get_user_favorites()                → favorite_dao.py
#   get_user_questions_count()          → question_dao.py
#   get_user_stats() (跨表聚合统计)       → analytics_dao.py
#   create_user_behavior_log()          → ❌ 改用 LogDAO.log()
#   get_user_behavior_logs()            → ❌ 改用 LogDAO.list(operator_id=...)
# ===========================================================================
