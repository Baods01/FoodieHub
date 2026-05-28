from typing import Optional
from datetime import datetime, timedelta
from jose import jwt

from config import settings
from dao.user_dao import UserDAO
from utils.auth import create_access_token
from utils.password import hash_password, verify_password
from schemas.users import (
    UserCreate, UserResponse, LoginResponse, UserUpdate,
)


class UserService:
    """用户业务逻辑"""

    @staticmethod
    async def register(data: UserCreate) -> UserResponse:
        dupe = await UserDAO.check_duplicate(data.username, data.phone, data.email)
        if dupe:
            labels = {"username": "用户名", "phone": "手机号", "email": "邮箱"}
            raise ValueError(f"{labels.get(dupe, dupe)}已存在")

        hashed = hash_password(data.password)
        user = await UserDAO.create(
            username=data.username, password=hashed,
            phone=data.phone, email=data.email,
        )
        return UserResponse.model_validate(user)

    @staticmethod
    async def login(login_type: str, account: str, password: str) -> LoginResponse:
        # 按登录类型调对应的 DAO 方法
        if login_type == "username":
            user = await UserDAO.get_by_username(account)
        elif login_type == "phone":
            user = await UserDAO.get_by_phone(account)
        elif login_type == "email":
            user = await UserDAO.get_by_email(account)
        else:
            raise ValueError("无效的登录方式")

        if not user:
            raise ValueError("账号或密码错误")

        if not verify_password(password, user.password):
            raise ValueError("账号或密码错误")

        if not user.is_active:
            raise ValueError("您的账户已被封禁")

        token = create_access_token(user.id)
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    @staticmethod
    async def authenticate(account: str, password: str) -> Optional[UserResponse]:
        """OAuth2 表单登录专用。"""
        user = await UserDAO.get_by_account_include_banned(account)
        if not user or not verify_password(password, user.password):
            return None
        return UserResponse.model_validate(user)

    @staticmethod
    async def get_by_id(user_id: int) -> Optional[UserResponse]:
        user = await UserDAO.get_by_id(user_id)
        return UserResponse.model_validate(user) if user else None

    @staticmethod
    async def update_profile(user_id: int, data: UserUpdate) -> Optional[UserResponse]:
        update_dict = data.model_dump(exclude_unset=True)
        if not update_dict:
            return await UserService.get_by_id(user_id)
        user = await UserDAO.update(user_id, **update_dict)
        return UserResponse.model_validate(user) if user else None

    @staticmethod
    async def ban_user(user_id: int) -> bool:
        user = await UserDAO.update(user_id, is_banned=True)
        return user is not None

    @staticmethod
    async def unban_user(user_id: int) -> bool:
        user = await UserDAO.update(user_id, is_banned=False)
        return user is not None

    @staticmethod
    async def delete_account(user_id: int) -> bool:
        return await UserDAO.delete(user_id)

    @staticmethod
    async def list(
        is_active: Optional[bool] = None,
        is_banned: Optional[bool] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        return await UserDAO.list(
            is_active=is_active, is_banned=is_banned,
            keyword=keyword, page=page, page_size=page_size,
        )
