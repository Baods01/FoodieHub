from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Optional

from config import settings
from models.users import Users
from schemas.users import UserResponse

# OAuth2 密码 bearer 方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login", auto_error=False)


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[UserResponse]:
    """
    获取当前登录用户（可选）
    - 如果 token 无效或过期，返回 None（游客）
    - 如果用户不存在或被禁用，返回 None
    - 如果登录成功，返回用户信息
    """
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    user = await Users.get_or_none(id=int(user_id), is_active=True)
    if user:
        return UserResponse.model_validate(user)
    return None


async def require_login(user: Optional[UserResponse] = Depends(get_current_user)) -> UserResponse:
    """
    要求用户必须登录
    - 游客访问时抛出 401 错误
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录后再进行操作",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_admin(user: UserResponse = Depends(require_login)) -> UserResponse:
    """
    要求用户必须是管理员
    - 如果不是管理员，抛出 403 错误
    """
    if user.role != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return user