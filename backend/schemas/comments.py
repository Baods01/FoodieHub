from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ 评论请求 ============

class CommentCreateRequest(BaseModel):
    """创建评论请求（纯文字）"""
    content: str = Field(..., min_length=1, max_length=500, description="评论内容（必填，1-500字符）")


# ============ 评论响应 ============

class CommentImageResponse(BaseModel):
    """评论关联的图片响应"""
    id: int = Field(description="图片ID")
    url: str = Field(description="图片URL")
    created_at: datetime = Field(description="上传时间")

    class Config:
        from_attributes = True


class CommentUserResponse(BaseModel):
    """评论用户响应"""
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    avatar: Optional[str] = Field(default=None, description="头像")

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """评论响应"""
    id: int = Field(description="评论ID")
    shop_id: int = Field(description="店铺ID")
    user: CommentUserResponse = Field(description="用户信息")
    type: str = Field(description="评论类型：comment=评论, question=提问")
    parent_id: Optional[int] = Field(default=None, description="父评论ID")
    content: str = Field(description="评论内容")
    like_count: int = Field(description="点赞数")
    reply_count: int = Field(description="回复数")
    images: List[CommentImageResponse] = Field(default=[], description="评论关联的图片")
    has_liked: bool = Field(default=False, description="是否已点赞")
    created_at: datetime = Field(description="评论时间")
    updated_at: datetime = Field(description="最后更新时间")

    class Config:
        from_attributes = True