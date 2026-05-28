from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class LogResponse(BaseModel):
    id: int
    operator_id: Optional[int]
    operator_name: Optional[str]
    action: str
    target_type: str
    target_id: Optional[int]
    detail: Optional[dict]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    items: list[LogResponse]
    total: int
    page: int
    page_size: int
