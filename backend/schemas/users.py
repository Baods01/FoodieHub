from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
import re


# ============ 请求模型 ============

class UserCreate(BaseModel):
    """用户注册请求"""
    username: str = Field(min_length=2, max_length=50, description="登录用户名")
    password: str = Field(min_length=6, max_length=128, description="密码")
    phone: str = Field(max_length=20, description="手机号")
    email: EmailStr = Field(description="电子邮箱")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[\w\u4e00-\u9fa5]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和中文')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class UserLogin(BaseModel):
    """用户登录请求"""
    account: str = Field(description="用户名/手机号/邮箱")
    password: str = Field(min_length=6, max_length=128, description="密码")
    remember_me: bool = Field(default=False, description="记住我")


class UserPhoneLogin(BaseModel):
    """手机号登录请求"""
    phone: str = Field(description="手机号")
    password: str = Field(min_length=6, max_length=128, description="密码")


class UserEmailLogin(BaseModel):
    """邮箱登录请求"""
    email: EmailStr = Field(description="邮箱")
    password: str = Field(min_length=6, max_length=128, description="密码")


class PasswordChange(BaseModel):
    """密码修改请求"""
    old_password: str = Field(min_length=6, description="旧密码")
    new_password: str = Field(min_length=6, max_length=128, description="新密码")


class UserUpdate(BaseModel):
    """用户信息更新请求"""
    nickname: Optional[str] = Field(default=None, min_length=2, max_length=30, description="昵称（用户显示名）")
    avatar: Optional[str] = Field(default=None, max_length=255, description="头像图片URL")
    bio: Optional[str] = Field(default=None, max_length=500, description="个人简介")
    gender: Optional[str] = Field(default=None, pattern="^(male|female|other)$", description="性别：male=男性，female=女性，other=其他")


class PhoneUpdate(BaseModel):
    """手机号更新请求"""
    new_phone: str = Field(max_length=20, description="新手机号")
    password: str = Field(description="当前密码，用于验证")

    @field_validator('new_phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class EmailUpdate(BaseModel):
    """邮箱更新请求"""
    new_email: EmailStr = Field(description="新邮箱")
    password: str = Field(description="当前密码，用于验证")


# ============ 响应模型 ============

class UserResponse(BaseModel):
    """用户信息响应（不包含密码）"""
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    nickname: Optional[str] = Field(default=None, description="昵称（用户显示名）")
    phone: Optional[str] = Field(default=None, description="手机号")
    email: Optional[str] = Field(default=None, description="邮箱")
    avatar: Optional[str] = Field(default=None, description="头像URL")
    bio: Optional[str] = Field(default=None, description="个人简介")
    gender: Optional[str] = Field(default=None, description="性别：male/female/other")
    role: int = Field(description="角色：0=普通用户，1=管理员")
    created_at: datetime = Field(description="注册时间")

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(description="用户信息")
    expires_in: int = Field(description="过期时间（秒）")


class UserComment(BaseModel):
    """用户评论信息"""
    comment_id: int = Field(description="评论ID")
    content: str = Field(description="评论内容")
    created_at: datetime = Field(description="评论时间")
    reply_count: int = Field(default=0, description="回复数")
    like_count: int = Field(default=0, description="点赞数")
    shop_id: int = Field(description="店铺ID")
    shop_name: str = Field(description="店铺名称")


class UserFavorite(BaseModel):
    """用户收藏信息"""
    favorite_id: int = Field(description="收藏ID")
    sort_order: int = Field(default=0, description="排序序号")
    created_at: datetime = Field(description="收藏时间")
    shop_id: int = Field(description="店铺ID")
    shop_name: str = Field(description="店铺名称")


class UserStats(BaseModel):
    """用户统计数据"""
    comment_count: int = Field(default=0, description="评论数")
    rating_count: int = Field(default=0, description="评分数")
    favorite_count: int = Field(default=0, description="收藏数")
    activity_count: int = Field(default=0, description="动态数")


class ViewHistoryItem(BaseModel):
    """浏览历史记录项"""
    shop_id: int = Field(description="店铺ID")
    shop_name: str = Field(description="店铺名称")
    shop_cover: Optional[str] = Field(default=None, description="店铺封面图")
    region: Optional[str] = Field(default=None, description="区域")
    viewed_at: datetime = Field(description="浏览时间")


class ViewHistoryResponse(BaseModel):
    """浏览历史记录响应"""
    items: List[ViewHistoryItem] = Field(description="浏览历史记录列表")
    total: int = Field(description="总记录数")
    has_more: bool = Field(description="是否有更多记录")


class UserProfileResponse(BaseModel):
    """个人主页响应"""
    user: UserResponse = Field(description="用户信息")
    stats: UserStats = Field(description="统计数据")
