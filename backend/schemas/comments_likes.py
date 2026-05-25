from pydantic import BaseModel
from datetime import datetime


class CommentLikeCreate(BaseModel):
    """点赞请求模型"""
    comment_id: int


class CommentLikeResponse(BaseModel):
    """点赞响应模型"""
    id: int
    comment_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True