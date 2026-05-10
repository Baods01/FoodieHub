from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from config import settings
from dao.user_dao import UserDAO
from schemas.users import (
    UserCreate, UserLogin, UserResponse, LoginResponse,
    UserUpdate, UserProfileResponse, UserStats
)
from services.password_service import PasswordService

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
    async def login(login_data: UserLogin) -> LoginResponse:
        """
        用户登录
        - 按用户名/手机号/邮箱查找用户
        - 验证密码
        - 生成 JWT 令牌
        """
        # 使用 DAO 层查找用户
        user = await UserDAO.find_by_account(login_data.account)
        if not user:
            raise ValueError("账号或密码错误")

        # 验证密码
        if not PasswordService.verify(login_data.password, user.password):
            raise ValueError("账号或密码错误")

        # 生成 JWT 令牌
        if login_data.remember_me:
            expires_days = settings.REMEMBER_ME_EXPIRE_DAYS
        else:
            expires_days = settings.ACCESS_TOKEN_EXPIRE_MINUTES / (60 * 24)  # 分钟转天

        expires_delta = timedelta(days=expires_days)
        expire = datetime.utcnow() + expires_delta

        payload = {
            "sub": str(user.id),
            "exp": expire,
            "type": "access"
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        # 构建用户响应
        user_response = UserResponse.model_validate(user)

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=user_response,
            expires_in=int(expires_delta.total_seconds())
        )

    @staticmethod
    async def authenticate(username: str, password: str):
        """
        用户认证（OAuth2 格式）
        - 根据用户名查找用户
        - 验证密码
        - 返回用户对象（用于生成 token）
        """
        from dao.user_dao import UserDAO
        
        user = await UserDAO.find_by_username(username)
        if not user:
            return None
        
        if not PasswordService.verify(password, user.password):
            return None
        
        return user

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[UserResponse]:
        """根据 ID 获取用户"""
        user = await UserDAO.find_by_id(user_id)
        if user:
            return UserResponse.model_validate(user)
        return None

    @staticmethod
    async def update_profile(user_id: int, update_data: UserUpdate) -> UserResponse:
        """
        更新用户个人信息
        - 支持更新头像和简介
        """
        update_dict = update_data.model_dump(exclude_unset=True)
        user = await UserDAO.update_user(user_id, **update_dict)
        if not user:
            raise ValueError("用户不存在")
        return UserResponse.model_validate(user)

    @staticmethod
    async def delete_account(user_id: int) -> None:
        """
        软删除用户账号
        """
        success = await UserDAO.delete_user(user_id)
        if not success:
            raise ValueError("用户不存在")

    @staticmethod
    async def get_profile(user_id: int) -> UserProfileResponse:
        """
        获取用户个人主页信息
        - 包含用户基本信息和统计数据
        """
        # 获取用户基本信息
        user = await UserDAO.find_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 获取用户统计数据
        stats_dict = await UserDAO.get_user_stats(user_id)
        stats = UserStats(**stats_dict)
        
        # 构建响应
        user_response = UserResponse.model_validate(user)
        return UserProfileResponse(user=user_response, stats=stats)
