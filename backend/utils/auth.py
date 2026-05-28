from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import traceback

from config import settings
from models.users import Users
from schemas.users import UserResponse


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(user_id)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login", auto_error=False, scheme_name="OAuth2PasswordBearer",
)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[UserResponse]:
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


async def require_login(
    user: Optional[UserResponse] = Depends(get_current_user),
) -> UserResponse:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录后再进行操作",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_admin(
    user: UserResponse = Depends(require_login),
) -> UserResponse:
    if user.role != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return user
