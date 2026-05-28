from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# ============ 请求模型 ============

class MenuItemCreateRequest(BaseModel):
    """创建菜单项请求"""
    name: str = Field(min_length=1, max_length=100, description="菜品名称")
    price: Optional[float] = Field(default=None, ge=0, description="价格")
    description: Optional[str] = Field(default=None, max_length=500, description="菜品描述")


class MenuItemAddRequest(BaseModel):
    """添加菜单项请求"""
    name: str = Field(..., min_length=1, max_length=100, description="菜品名称")
    price: float = Field(..., gt=0, description="价格（必填）")
    description: Optional[str] = Field(default=None, max_length=500, description="菜品描述（可选）")


class ShopCreate(BaseModel):
    """创建店铺请求"""
    name: str = Field(min_length=1, max_length=100, description="店铺名称")
    dict_data_ids: List[int] = Field(
        ..., min_length=2,
        description="字典数据ID列表，至少包含一个品类ID和一个区域ID"
    )
    menu_items: Optional[List[MenuItemCreateRequest]] = Field(default=None, description="初始菜单项（可选）")


class ShopUpdate(BaseModel):
    """更新店铺请求（管理员）"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="店铺名称")
    is_active: Optional[bool] = Field(default=None, description="是否启用（软删除）")
    dict_data_ids: Optional[List[int]] = Field(
        default=None,
        description="字典数据ID列表（整体替换店铺标签，传空列表则清空标签）"
    )


class RatingCreate(BaseModel):
    """评分请求"""
    score: int = Field(ge=1, le=5, description="评分值（1-5）")


# ============ 响应模型 ============

class RatingDistribution(BaseModel):
    """评分分布统计"""
    star_1: int = Field(default=0, description="1星评分人数")
    star_2: int = Field(default=0, description="2星评分人数")
    star_3: int = Field(default=0, description="3星评分人数")
    star_4: int = Field(default=0, description="4星评分人数")
    star_5: int = Field(default=0, description="5星评分人数")
    total: int = Field(default=0, description="总评分人数")

    class Config:
        from_attributes = True


class MenuItemResponse(BaseModel):
    """菜单项响应"""
    id: int = Field(description="菜单项ID")
    shop_id: int = Field(description="所属店铺ID")
    name: str = Field(description="菜品名称")
    price: Optional[float] = Field(default=None, description="价格")
    description: Optional[str] = Field(default=None, description="菜品描述")
    created_at: datetime = Field(description="创建时间")

    class Config:
        from_attributes = True


class RatingResponse(BaseModel):
    """评分响应"""
    id: int = Field(description="评分ID")
    user_id: int = Field(description="评分用户ID")
    shop_id: int = Field(description="店铺ID")
    score: int = Field(description="评分值")
    created_at: datetime = Field(description="评分时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


class DictDataSimpleResponse(BaseModel):
    """字典数据简略响应（店铺标签用）"""
    id: int = Field(description="字典数据ID")
    name: str = Field(description="标签名称")
    extra: Optional[dict] = Field(default=None, description="扩展信息")

    class Config:
        from_attributes = True


class ImageBriefResponse(BaseModel):
    """图片简略响应（店铺详情/列表用）"""
    id: int = Field(description="图片ID")
    url: str = Field(description="图片URL")

    class Config:
        from_attributes = True


class ShopResponse(BaseModel):
    """店铺详情响应"""
    id: int = Field(description="店铺ID")
    name: str = Field(description="店铺名称")
    view_count: int = Field(description="浏览量")
    favorite_count: int = Field(description="收藏数")
    comment_count: int = Field(description="评论数")
    average_rating: float = Field(default=0.0, description="平均评分")
    rating_distribution: Optional[RatingDistribution] = Field(default=None, description="评分分布统计")
    aliases: Optional[List[str]] = Field(default=None, description="别名列表")
    merged_into_id: Optional[int] = Field(default=None, description="合并后店铺ID")
    is_banned: bool = Field(default=False, description="是否被封禁")
    dict_data: Optional[List[DictDataSimpleResponse]] = Field(default=None, description="关联的字典标签")
    menu_items: Optional[List[MenuItemResponse]] = Field(default=None, description="菜单列表")
    images: Optional[List[ImageBriefResponse]] = Field(default=None, description="图片列表")
    is_favorited: bool = Field(default=False, description="当前用户是否已收藏")
    user_rating: Optional[RatingResponse] = Field(default=None, description="当前用户的评分")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


class ShopListItem(BaseModel):
    """店铺列表项"""
    id: int = Field(description="店铺ID")
    name: str = Field(description="店铺名称")
    average_rating: float = Field(default=0.0, description="平均评分")
    view_count: int = Field(description="浏览量")
    favorite_count: int = Field(description="收藏数")
    comment_count: int = Field(description="评论数")
    cover_image: Optional[str] = Field(default=None, description="封面图片URL")
    dict_data: Optional[List[DictDataSimpleResponse]] = Field(default=None, description="字典标签")
    is_favorited: bool = Field(default=False, description="当前用户是否已收藏")
    created_at: datetime = Field(description="创建时间")

    class Config:
        from_attributes = True
