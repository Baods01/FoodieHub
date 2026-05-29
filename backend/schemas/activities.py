from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ActivityResponse(BaseModel):
    """动态响应"""
    id: int
    user_id: int = Field(description="用户ID")
    type: str = Field(description="动态类型")
    target_id: int
    target_type: str
    content: Optional[str] = Field(default=None, description="动态摘要")
    shop_id: Optional[int] = Field(default=None, description="关联店铺ID（前端跳转用）")
    shop_name: Optional[str] = Field(default=None, description="关联店铺名称")
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """动态列表响应"""
    items: list[ActivityResponse]
    total: int
    page: int
    page_size: int
