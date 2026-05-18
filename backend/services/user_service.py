from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from config import settings
from dao.user_dao import UserDAO
from schemas.users import (
    UserCreate, UserResponse, LoginResponse,
    UserUpdate, UserProfileResponse, UserStats,
    UserComment, UserFavorite
)
from services.password_service import PasswordService


# 敏感词列表（可扩展）
SENSITIVE_WORDS = [
    # 添加敏感词
    # "敏感词1",
    # "敏感词2",
]

# 密码验证上下文（用于 OAuth2 登录）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """用户业务逻辑服务"""

    @staticmethod
    async def register(user_data: UserCreate) -> UserResponse:
        """
        用户注册
        - 校验用户名/手机号/邮箱是否已存在
        - 加密密码并创建用户
        - 返回用户信息（不含密码）
        """
        # 使用 DAO 层检查重复
        duplicate_field = await UserDAO.check_duplicate(
            username=user_data.username,
            phone=user_data.phone,
            email=user_data.email
        )
        if duplicate_field:
            field_names = {
                "username": "用户名",
                "phone": "手机号",
                "email": "邮箱"
            }
            raise ValueError(f"{field_names.get(duplicate_field, duplicate_field)}已存在")

        # 加密密码
        hashed_password = PasswordService.hash(user_data.password)

        # 使用 DAO 层创建用户
        user = await UserDAO.create_user(
            username=user_data.username,
            password=hashed_password,
            phone=user_data.phone,
            email=user_data.email,
            role=0  # 普通用户
        )

        return UserResponse.model_validate(user)

    @staticmethod
    async def authenticate(username: str, password: str):
        """
        用户认证（OAuth2 格式）
        - 根据用户名查找用户（包括被封禁用户）
        - 验证密码
        - 检查账户状态（封禁用户无法登录）
        - 返回用户对象（用于生成 token）
        """
        from dao.user_dao import UserDAO
        
        # 使用 find_by_account_include_banned 查找用户（包括被封禁用户）
        user = await UserDAO.find_by_account_include_banned(username)
        if not user:
            return None
        
        if not PasswordService.verify(password, user.password):
            return None
        
        # 检查用户是否被封禁
        if not user.is_active:
            # 查询封禁记录获取封禁原因
            from dao.ban_dao import BanDAO
            ban_record = await BanDAO.get_active_ban("user", user.id)
            if ban_record:
                reason = ban_record.reason or "未说明原因"
                raise ValueError(f"您的账户已被封禁，封禁原因：{reason}")
            else:
                raise ValueError("您的账户已被封禁")
        
        return user

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[UserResponse]:
        """根据 ID 获取用户"""
        user = await UserDAO.find_by_id(user_id)
        if user:
            return UserResponse.model_validate(user)
        return None

    @staticmethod
    async def delete_account(user_id: int) -> None:
        """
        软删除用户账号
        """
        success = await UserDAO.delete_user(user_id)
        if not success:
            raise ValueError("用户不存在")

    @staticmethod
    async def get_profile(user_id: int) -> dict:
        """
        获取用户个人主页信息
        - 包含用户基本信息、统计数据和详细列表
        """
        from schemas.users import UserProfileResponse, UserComment, UserFavorite
        
        # 获取用户基本信息
        user = await UserDAO.find_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 获取用户统计数据
        stats_dict = await UserDAO.get_user_stats(user_id)
        
        # 获取用户评论列表（最新10条）
        comments = await UserDAO.get_user_comments(user_id, limit=10, offset=0)
        comment_list = [UserComment(**c) for c in comments]
        
        # 获取用户收藏列表（最新10条）
        favorites = await UserDAO.get_user_favorites(user_id, limit=10, offset=0)
        favorite_list = [UserFavorite(**f) for f in favorites]
        
        # 获取用户问答数
        question_count = await UserDAO.get_user_questions_count(user_id)
        
        return {
            "user": UserResponse.model_validate(user),
            "stats": UserStats(**stats_dict),
            "comments": comment_list,
            "favorites": favorite_list,
            "question_count": question_count
        }

    @staticmethod
    async def get_profile_with_details(user_id: int) -> dict:
        """
        获取用户个人主页完整信息
        - 包含用户基本信息、统计数据和详细列表
        """
        from schemas.users import UserProfileResponse
        
        # 获取用户基本信息
        user = await UserDAO.find_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 获取用户统计数据
        stats_dict = await UserDAO.get_user_stats(user_id)
        
        # 获取用户评论列表（最新10条）
        comments = await UserDAO.get_user_comments(user_id, limit=10, offset=0)
        
        # 获取用户收藏列表（最新10条）
        favorites = await UserDAO.get_user_favorites(user_id, limit=10, offset=0)
        
        # 获取用户问答数
        question_count = await UserDAO.get_user_questions_count(user_id)
        
        return {
            "user": UserResponse.model_validate(user),
            "stats": stats_dict,
            "comments": comments,
            "favorites": favorites,
            "question_count": question_count
        }

    @staticmethod
    def filter_sensitive_words(text: Optional[str]) -> Optional[str]:
        """
        过滤敏感词
        Args:
            text: 原始文本
        Returns:
            过滤后的文本
        """
        if not text:
            return text
        for word in SENSITIVE_WORDS:
            text = text.replace(word, "*" * len(word))
        return text

    @staticmethod
    async def update_profile(user_id: int, update_data: UserUpdate) -> UserResponse:
        """
        更新用户个人信息
        - 支持更新昵称、头像、简介、性别
        - 自动过滤敏感词
        """
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # 过滤敏感词（昵称和简介）
        if "nickname" in update_dict and update_dict["nickname"]:
            update_dict["nickname"] = UserService.filter_sensitive_words(update_dict["nickname"])
        if "bio" in update_dict and update_dict["bio"]:
            update_dict["bio"] = UserService.filter_sensitive_words(update_dict["bio"])
        
        user = await UserDAO.update_user(user_id, **update_dict)
        if not user:
            raise ValueError("用户不存在")
        return UserResponse.model_validate(user)

    @staticmethod
    async def update_avatar(user_id: int, avatar_url: str) -> UserResponse:
        """
        更新用户头像
        Args:
            user_id: 用户ID
            avatar_url: 头像URL
        Returns:
            更新后的用户信息
        """
        user = await UserDAO.update_user(user_id, avatar=avatar_url)
        if not user:
            raise ValueError("用户不存在")
        return UserResponse.model_validate(user)

    @staticmethod
    async def log_user_behavior(
        user_id: int,
        behavior_type: str,
        target_type: str,
        target_id: int
    ) -> None:
        """
        记录用户行为日志
        
        Args:
            user_id: 用户ID
            behavior_type: 行为类型（如 ban_shop、unban_user 等）
            target_type: 目标类型（如 shop、user 等）
            target_id: 目标ID
        """
        from models.logs import UserBehaviorLogs
        
        await UserBehaviorLogs.create(
            user_id=user_id,
            behavior_type=behavior_type,
            target_type=target_type,
            target_id=target_id
        )
