from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .shops import ShopListItem


# ============ 请求模型 ============

class FavoriteCreate(BaseModel):
    """收藏店铺请求"""
    shop_id: int = Field(description="店铺ID")


class FavoriteReorderRequest(BaseModel):
    """收藏夹排序调整请求"""
    shop_id: int = Field(description="店铺ID")
    sort_order: int = Field(description="新排序序号")


class FavoriteBatchReorderRequest(BaseModel):
    """收藏夹批量排序请求"""
    shop_ids: list[int] = Field(description="店铺ID列表（按顺序排列）")


# ============ 响应模型 ============

class FavoriteResponse(BaseModel):
    """收藏响应"""
    id: int = Field(description="收藏ID")
    user_id: int = Field(description="用户ID")
    shop_id: int = Field(description="店铺ID")
    sort_order: int = Field(description="排序序号")
    shop: Optional[ShopListItem] = Field(default=None, description="店铺信息")
    created_at: datetime = Field(description="收藏时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True