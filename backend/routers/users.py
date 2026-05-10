from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from schemas.users import (
    UserCreate, UserResponse, UserUpdate, UserProfileResponse
)
from schemas.common import ResponseModel
from services.user_service import UserService
from dependencies.auth import create_access_token, get_current_user

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


@router.post("/login", summary="用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录接口（OAuth2 格式）
    - 支持 Swagger UI 的 "Authorize" 功能
    - 接收表单数据：username, password
    - 返回 JWT token（OAuth2 标准格式）
    """
    try:
        user = await UserService.authenticate(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名或密码错误"
            )
        
        access_token = create_access_token(user.id)
        # 返回 OAuth2 标准格式（不使用 ResponseModel 包装）
        return JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer"
            }
        )
    except HTTPException:
        raise
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


@router.put("/me", response_model=ResponseModel[UserResponse], summary="更新个人信息")
async def update_me(
    update_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    更新用户个人信息
    - 支持更新头像和简介
    - 需登录
    """
    try:
        user = await UserService.update_profile(current_user.id, update_data)
        return ResponseModel.success(data=user, message="更新成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/me", response_model=ResponseModel[dict], summary="注销账号")
async def delete_me(current_user: UserResponse = Depends(get_current_user)):
    """
    软删除用户账号
    - 需登录
    - 删除后不可恢复（软删除，数据保留）
    """
    try:
        await UserService.delete_account(current_user.id)
        return ResponseModel.success(data={}, message="账号注销成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me/profile", response_model=ResponseModel[UserProfileResponse], summary="获取个人主页")
async def get_my_profile(current_user: UserResponse = Depends(get_current_user)):
    """
    获取用户个人主页信息
    - 包含用户基本信息和统计数据（店铺数、评论数、收藏数等）
    - 需登录
    """
    try:
        profile = await UserService.get_profile(current_user.id)
        return ResponseModel.success(data=profile, message="获取成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
