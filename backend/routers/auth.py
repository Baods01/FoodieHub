from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from schemas.users import (
    UserCreate, UserResponse, UserUpdate, UserPhoneLogin, UserEmailLogin,
)
from schemas.common import ResponseModel
from services import UserService
from utils.auth import create_access_token, get_current_user, require_login

router = APIRouter(prefix="/users", tags=["用户模块"])


@router.post("/register", response_model=ResponseModel[UserResponse])
async def register(data: UserCreate):
    try:
        user = await UserService.register(data)
        return ResponseModel.success(data=user, message="注册成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", summary="OAuth2 表单登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserService.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账号或密码错误",
        )
    token = create_access_token(user.id)
    return JSONResponse(content={"access_token": token, "token_type": "bearer"})


@router.post("/login-phone")
async def login_phone(data: UserPhoneLogin):
    try:
        resp = await UserService.login(data.phone, data.password)
        return JSONResponse(content={"access_token": resp.access_token, "token_type": "bearer"})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login-email")
async def login_email(data: UserEmailLogin):
    try:
        resp = await UserService.login(data.email, data.password)
        return JSONResponse(content={"access_token": resp.access_token, "token_type": "bearer"})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=ResponseModel)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return ResponseModel.success(data=current_user, message="获取成功")


@router.put("/me", response_model=ResponseModel[UserResponse])
async def update_me(data: UserUpdate, current_user: UserResponse = Depends(require_login)):
    try:
        user = await UserService.update_profile(current_user.id, data)
        return ResponseModel.success(data=user, message="更新成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
