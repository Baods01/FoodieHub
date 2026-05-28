from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class EditRequestCreate(BaseModel):
    shop_id: int
    proposed_data: dict = Field(description="提议修改的字段（Service 层构造 JSON）")


class EditRequestResponse(BaseModel):
    id: int
    shop_id: int
    user_id: int
    proposed_data: dict
    status: str
    admin_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EditRequestListResponse(BaseModel):
    items: list[EditRequestResponse]
    total: int
    page: int
    page_size: int
