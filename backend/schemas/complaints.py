from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ComplaintCreateRequest(BaseModel):
    complainant_type: str = Field(
        ..., pattern="^(comment|shop|image)$",
        description="被举报内容类型：comment、shop、image",
    )
    complainant_id: int = Field(..., ge=1, description="被举报内容ID")
    reason_code: str = Field(..., max_length=50, description="举报原因编码")
    description: Optional[str] = Field(None, max_length=500, description="补充说明")


class ComplaintHandleRequest(BaseModel):
    action: str = Field(
        ..., pattern="^(delete_comment|ban_shop|remove_image|dismiss)$",
        description="处理动作",
    )
    result_description: Optional[str] = Field(None, description="处理结果描述")


class ComplaintResponse(BaseModel):
    id: int
    user_id: int
    username: Optional[str] = Field(default=None, description="举报发起用户名")
    complainant_type: str
    complainant_id: int
    reason_code: str
    description: Optional[str]
    status: str
    admin_id: Optional[int]
    action: Optional[str]
    result_description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComplaintListResponse(BaseModel):
    items: list[ComplaintResponse]
    total: int
    page: int
    page_size: int


class ComplaintStatsResponse(BaseModel):
    pending: int
    approved: int
    rejected: int
    total: int
