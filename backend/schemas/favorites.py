from datetime import datetime
from typing import List
from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    """收藏创建请求"""
    shop_id: int


class FavoriteResponse(BaseModel):
    """收藏响应"""
    id: int
    user_id: int
    shop_id: int
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteReorderRequest(BaseModel):
    """收藏重新排序请求"""
    favorite_id: int
    sort_order: int


class FavoriteBatchReorderRequest(BaseModel):
    """批量收藏重新排序请求"""
    favorites: List[FavoriteReorderRequest]


class FavoriteActionResponse(BaseModel):
    """收藏操作响应（通用）"""
    success: bool
    message: str
    is_favorited: bool  # 当前状态
    favorite_count: int  # 店铺收藏总数


class UserFavoritesResponse(BaseModel):
    """用户收藏列表响应"""
    total: int
    favorites: List[FavoriteResponse]