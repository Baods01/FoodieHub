from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============ 用户缩略信息（评论区/问答区专用） ============

class InteractionUserBrief(BaseModel):
    """评论/问答中的用户简略信息"""
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    avatar: Optional[str] = Field(default=None, description="头像URL")


# ==============================
#  评论区
# ==============================

class CommentCreate(BaseModel):
    """创建一级评论"""
    content: str = Field(min_length=1, max_length=2000, description="评论内容")
    image_id: Optional[int] = Field(default=None, description="附带图片ID（可选，上传后返回）")


class CommentResponse(BaseModel):
    """一级评论响应"""
    id: int
    shop_id: int
    user: Optional[InteractionUserBrief] = Field(default=None, description="评论作者")
    content: str
    image: Optional[str] = Field(default=None, description="评论图片URL")
    like_count: int
    reply_count: int
    has_liked: bool = Field(default=False, description="当前用户是否已点赞")
    created_at: datetime

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """一级评论列表"""
    items: list[CommentResponse]
    total: int
    page: int
    page_size: int


class ReplyCreate(BaseModel):
    """创建二级回复"""
    content: str = Field(min_length=1, max_length=2000, description="回复内容")
    reply_to_user_id: Optional[int] = Field(default=None, description="被回复用户ID（用于 @username 前缀）")


class ReplyResponse(BaseModel):
    """二级回复响应"""
    id: int
    comment_id: int
    user: Optional[InteractionUserBrief] = Field(default=None, description="回复作者")
    content: str
    reply_to_user: Optional[InteractionUserBrief] = Field(default=None, description="被回复用户")
    like_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReplyListResponse(BaseModel):
    """二级回复列表"""
    items: list[ReplyResponse]


# ==============================
#  问答区
# ==============================

class QuestionCreate(BaseModel):
    """创建一级问题"""
    title: str = Field(min_length=1, max_length=100, description="问题概括（短）")
    content: Optional[str] = Field(default=None, description="问题描述（长，可选）")


class QuestionResponse(BaseModel):
    """一级问题响应"""
    id: int
    shop_id: int
    user: Optional[InteractionUserBrief] = Field(default=None, description="提问用户")
    title: str
    content: Optional[str]
    like_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    """一级问题列表"""
    items: list[QuestionResponse]
    total: int
    page: int
    page_size: int


class AnswerCreate(BaseModel):
    """创建二级回答"""
    content: str = Field(min_length=1, max_length=2000, description="回答内容")
    reply_to_user_id: Optional[int] = Field(default=None, description="被回复用户ID（用于 @username 前缀）")


class AnswerResponse(BaseModel):
    """二级回答响应"""
    id: int
    question_id: int
    user: Optional[InteractionUserBrief] = Field(default=None, description="回答作者")
    content: str
    reply_to_user: Optional[InteractionUserBrief] = Field(default=None, description="被回复用户")
    like_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class AnswerListResponse(BaseModel):
    """二级回答列表"""
    items: list[AnswerResponse]


# ==============================
#  内容点赞
# ==============================

class LikeToggleRequest(BaseModel):
    """点赞切换请求"""
    entity_type: str = Field(description="内容类型：shop_comment / comment_reply / shop_question / question_answer")
    entity_id: int = Field(description="内容ID")


class LikeToggleResponse(BaseModel):
    """点赞切换响应"""
    is_liked: bool = Field(description="点赞后的状态")
    like_count: int = Field(description="当前点赞总数")
