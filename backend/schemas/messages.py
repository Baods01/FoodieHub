from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============ 请求模型 ============

class MessageMarkReadRequest(BaseModel):
    """标记消息已读请求"""
    message_ids: list[int] = Field(description="消息ID列表")


class MessageDeleteRequest(BaseModel):
    """删除消息请求"""
    message_ids: list[int] = Field(description="消息ID列表")


# ============ 响应模型 ============

class MessageUserResponse(BaseModel):
    """消息中的发送者信息"""
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    avatar: Optional[str] = Field(default=None, description="头像URL")

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """消息响应"""
    id: int = Field(description="消息ID")
    recipient_id: int = Field(description="接收用户ID")
    sender: Optional[MessageUserResponse] = Field(default=None, description="发送方（系统消息为空）")
    type: str = Field(description="消息类型")
    title: Optional[str] = Field(default=None, description="消息标题")
    content: str = Field(description="消息内容")
    related_entity_type: Optional[str] = Field(default=None, description="关联实体类型")
    related_entity_id: Optional[int] = Field(default=None, description="关联实体ID")
    is_read: bool = Field(default=False, description="是否已读")
    created_at: datetime = Field(description="发送时间")

    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    """未读消息数量响应"""
    unread_count: int = Field(description="未读消息数量")


class MessageTypesResponse(BaseModel):
    """消息类型列表响应"""
    types: list[str] = Field(description="消息类型列表")