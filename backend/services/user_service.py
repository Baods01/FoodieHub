from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from config import settings
from dao.user_dao import UserDAO
from schemas.users import UserCreate, UserLogin, UserResponse, LoginResponse
from services.password_service import PasswordService


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
    async def get_user_by_id(user_id: int) -> Optional[UserResponse]:
        """根据 ID 获取用户"""
        user = await UserDAO.find_by_id(user_id)
        if user:
            return UserResponse.model_validate(user)
        return None