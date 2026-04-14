from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional

from schemas.users import UserCreate, UserLogin, UserResponse, LoginResponse
from schemas.common import ResponseModel
from services.user_service import UserService
from dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["用户模块"])


@router.post("/register", response_model=ResponseModel[UserResponse], summary="用户注册")
async def register(user_data: UserCreate):
    """
    用户注册接口
    - 用户名、密码、手机号、邮箱必填
    - 密码自动加密存储
    """
    try:
        user = await UserService.register(user_data)
        return ResponseModel.success(data=user, message="注册成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=ResponseModel[LoginResponse], summary="用户登录")
async def login(login_data: UserLogin):
    """
    用户登录接口
    - 支持用户名/手机号/邮箱登录
    - 支持"记住我"功能（30天有效期）
    - account: 用户名/手机号/邮箱
    """
    try:
        result = await UserService.login(login_data)
        return ResponseModel.success(data=result, message="登录成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=ResponseModel[Optional[UserResponse]], summary="获取当前用户信息")
async def get_me(current_user: Optional[UserResponse] = Depends(get_current_user)):
    """
    获取当前用户信息
    - 已登录：返回用户信息
    - 未登录：返回 null（游客）
    """
    return ResponseModel.success(data=current_user, message="获取成功")