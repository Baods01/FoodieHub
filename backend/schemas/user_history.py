from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from schemas.shops import ShopListItem


class UserHistoryItem(BaseModel):
    """
    用户浏览历史记录项
    """
    id: int
    shop: ShopListItem
    viewed_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserHistoryListRequest(BaseModel):
    """
    浏览历史列表查询请求参数
    """
    page: int = 1
    page_size: int = 20
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    shop_id: Optional[int] = None


class UserHistoryListResponse(BaseModel):
    """
    浏览历史列表响应
    """
    items: List[UserHistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class DeleteHistoryRequest(BaseModel):
    """
    删除浏览历史请求参数
    """
    history_id: int


class ClearHistoryResponse(BaseModel):
    """
    清空浏览历史响应
    """
    deleted_count: int