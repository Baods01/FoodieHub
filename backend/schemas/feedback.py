from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class FeedbackCreateRequest(BaseModel):
    """用户提交反馈请求"""
    type: str = Field(..., pattern="^(complaint|edit_request)$",
                      description="complaint=举报 | edit_request=勘误")
    target_type: str = Field(..., pattern="^(shop|comment|image)$",
                             description="shop / comment / image")
    target_id: int = Field(..., ge=1, description="被反馈对象ID")
    reason_id: int = Field(..., ge=1, description="反馈原因ID（来自 dict_data）")
    description: Optional[str] = Field(None, max_length=1000, description="补充说明")


class FeedbackResponse(BaseModel):
    """反馈工单响应"""
    id: int
    user_id: int
    username: Optional[str] = Field(default=None)
    type: str
    target_type: str
    target_id: int
    reason_id: int
    description: Optional[str]
    status: str
    admin_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeedbackListResponse(BaseModel):
    """反馈列表响应"""
    items: list[FeedbackResponse]
    total: int
    page: int
    page_size: int
