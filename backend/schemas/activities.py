from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .users import UserResponse


# ============ 响应模型 ============

class ActivityResponse(BaseModel):
    """动态响应"""
    id: int = Field(description="动态ID")
    user: UserResponse = Field(description="产生动态的用户")
    type: str = Field(description="动态类型：rating、comment、question、answer、favorite、add_shop等")
    target_id: int = Field(description="关联目标ID")
    target_type: str = Field(description="目标实体类型")
    content: Optional[str] = Field(default=None, description="动态摘要")
    created_at: datetime = Field(description="创建时间")

    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """动态列表响应"""
    items: list[ActivityResponse] = Field(default=[], description="动态列表")
    has_more: bool = Field(default=False, description="是否还有更多数据")


class ActivityStats(BaseModel):
    """用户动态统计"""
    total_count: int = Field(description="动态总数")
    type_distribution: dict = Field(default={}, description="各类型动态数量分布")