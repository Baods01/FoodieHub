from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from schemas.users import (
    UserCreate, UserResponse, UserUpdate, UserLogin,
)
from schemas.common import ResponseModel
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from services import UserService, LogService
from utils.auth import create_access_token, get_current_user, require_login

router = APIRouter(prefix="/users", tags=["用户模块"])


@router.post("/register", response_model=ResponseModel[UserResponse])
async def register(data: UserCreate):
    try:
        user = await UserService.register(data)
        return ResponseModel.success(data=user, message="注册成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login/oauth", include_in_schema=False)
async def login_oauth(form_data: OAuth2PasswordRequestForm = Depends()):
    """Swagger UI Authorize 专用 — 接受 OAuth2 标准表单。"""
    try:
        resp = await UserService.login("username", form_data.username, form_data.password)
        return JSONResponse(content={"access_token": resp.access_token, "token_type": "bearer"})
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="账号或密码错误")


@router.post("/login", response_model=ResponseModel, summary="登录")
async def login(data: UserLogin):
    try:
        resp = await UserService.login(data.type, data.account, data.password)
        return ResponseModel.success(
            data={
                "access_token": resp.access_token,
                "token_type": resp.token_type,
                "user": resp.user,
            },
            message="登录成功",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class UserPublicProfile(BaseModel):
    """用户公开信息（他人可见）"""
    id: int
    username: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    created_at: datetime


@router.get("/{user_id}/profile", response_model=ResponseModel, summary="用户公开信息")
async def get_user_profile(user_id: int):
    from dao.user_dao import UserDAO
    user = await UserDAO.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    profile = UserPublicProfile(
        id=user.id,
        username=user.username,
        avatar=user.avatar,
        bio=user.bio,
        gender=user.gender,
        created_at=user.created_at,
    )
    return ResponseModel.success(data=profile, message="获取成功")


@router.get("/me", response_model=ResponseModel)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return ResponseModel.success(data=current_user, message="获取成功")


@router.put("/me", response_model=ResponseModel[UserResponse])
async def update_me(data: UserUpdate, current_user: UserResponse = Depends(require_login)):
    try:
        user = await UserService.update_profile(current_user.id, data)
        await LogService.log(action="update_profile", operator=current_user, target_type="user", target_id=current_user.id)
        return ResponseModel.success(data=user, message="更新成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
