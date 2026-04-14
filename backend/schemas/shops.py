from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============ 请求模型 ============

class ShopCreate(BaseModel):
    """创建店铺请求"""
    name: str = Field(min_length=1, max_length=100, description="店铺名称")
    description: Optional[str] = Field(default=None, max_length=2000, description="店铺描述")
    dict_data_ids: Optional[List[int]] = Field(default=None, description="字典数据ID列表（类别、点餐方式、位置类型等）")
    menu_items: Optional[List["MenuItemCreateRequest"]] = Field(default=None, description="初始菜单项")


class MenuItemCreateRequest(BaseModel):
    """创建菜单项请求"""
    name: str = Field(min_length=1, max_length=100, description="菜品名称")
    price: Optional[Decimal] = Field(default=None, ge=0, description="价格")
    description: Optional[str] = Field(default=None, max_length=500, description="菜品描述")


class ShopUpdate(BaseModel):
    """更新店铺请求（管理员）"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="店铺名称")
    description: Optional[str] = Field(default=None, max_length=2000, description="店铺描述")
    is_active: Optional[bool] = Field(default=None, description="是否启用（软删除）")


class RatingCreate(BaseModel):
    """评分请求"""
    score: int = Field(ge=1, le=5, description="评分值（1-5）")


class CommentCreate(BaseModel):
    """创建评论/提问请求"""
    type: str = Field(default="comment", pattern="^(comment|question)$", description="类型：comment=评论，question=提问")
    content: str = Field(min_length=1, max_length=2000, description="内容")
    parent_id: Optional[int] = Field(default=None, description="父评论ID（回复时填写）")


class CommentUpdate(BaseModel):
    """更新评论请求"""
    content: str = Field(min_length=1, max_length=2000, description="内容")


class ShopEditRequestCreate(BaseModel):
    """店铺信息修改申请请求"""
    proposed_data: dict = Field(description="提议修改的字段及新值，JSON格式")


class ShopMergeRequest(BaseModel):
    """店铺合并请求（管理员）"""
    shop_ids: List[int] = Field(min_length=2, max_length=5, description="参与合并的店铺ID列表（2-5个）")
    primary_shop_id: int = Field(description="主店铺ID（合并后保留的名称和描述）")


class ShopSearchRequest(BaseModel):
    """店铺搜索请求"""
    keyword: Optional[str] = Field(default=None, max_length=100, description="搜索关键词")
    category_ids: Optional[List[int]] = Field(default=None, description="类别筛选")
    dining_method_ids: Optional[List[int]] = Field(default=None, description="点餐方式筛选")
    min_rating: Optional[float] = Field(default=None, ge=0, le=5, description="最低评分筛选")
    is_oncampus: Optional[bool] = Field(default=None, description="校内/校外筛选")
    sort_by: str = Field(default="created_at", pattern="^(created_at|average_rating|view_count|favorite_count)$", description="排序字段")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="排序方向")


# ============ 响应模型 ============

class ImageResponse(BaseModel):
    """图片响应"""
    id: int = Field(description="图片ID")
    url: str = Field(description="图片URL")
    entity_type: str = Field(description="关联实体类型")
    entity_id: int = Field(description="关联实体ID")
    extra: Optional[dict] = Field(default=None, description="扩展信息")
    created_at: datetime = Field(description="上传时间")

    class Config:
        from_attributes = True


class MenuItemResponse(BaseModel):
    """菜单项响应"""
    id: int = Field(description="菜单项ID")
    shop_id: int = Field(description="所属店铺ID")
    name: str = Field(description="菜品名称")
    price: Optional[Decimal] = Field(default=None, description="价格")
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


class CommentUserResponse(BaseModel):
    """评论中的用户信息"""
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    avatar: Optional[str] = Field(default=None, description="头像URL")

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """评论响应"""
    id: int = Field(description="评论ID")
    shop_id: int = Field(description="店铺ID")
    user: Optional[CommentUserResponse] = Field(default=None, description="评论用户")
    type: str = Field(description="类型")
    parent_id: Optional[int] = Field(default=None, description="父评论ID")
    content: str = Field(description="内容")
    like_count: int = Field(description="点赞数")
    reply_count: int = Field(description="回复数")
    replies: Optional[List["CommentResponse"]] = Field(default=None, description="回复列表")
    has_liked: bool = Field(default=False, description="当前用户是否点赞")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


class DictDataSimpleResponse(BaseModel):
    """字典数据简略响应"""
    id: int = Field(description="字典数据ID")
    code: str = Field(description="编码")
    name: str = Field(description="名称")
    extra: Optional[dict] = Field(default=None, description="扩展信息")

    class Config:
        from_attributes = True


class ShopResponse(BaseModel):
    """店铺详情响应"""
    id: int = Field(description="店铺ID")
    name: str = Field(description="店铺名称")
    description: Optional[str] = Field(default=None, description="店铺描述")
    view_count: int = Field(default=0, description="浏览量")
    favorite_count: int = Field(default=0, description="收藏数")
    comment_count: int = Field(default=0, description="评论数")
    average_rating: Decimal = Field(default=0.0, description="平均评分")
    aliases: Optional[List[str]] = Field(default=None, description="别名列表")
    merged_into_id: Optional[int] = Field(default=None, description="合并后店铺ID")
    dict_data: Optional[List[DictDataSimpleResponse]] = Field(default=None, description="关联的字典数据（类别、点餐方式等）")
    menu_items: Optional[List[MenuItemResponse]] = Field(default=None, description="菜单列表")
    images: Optional[List[ImageResponse]] = Field(default=None, description="图片列表")
    is_favorited: bool = Field(default=False, description="当前用户是否已收藏")
    user_rating: Optional[RatingResponse] = Field(default=None, description="当前用户的评分")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


class ShopListItem(BaseModel):
    """店铺列表项（简化版）"""
    id: int = Field(description="店铺ID")
    name: str = Field(description="店铺名称")
    description: Optional[str] = Field(default=None, description="店铺描述")
    average_rating: Decimal = Field(default=0.0, description="平均评分")
    view_count: int = Field(description="浏览量")
    favorite_count: int = Field(description="收藏数")
    comment_count: int = Field(description="评论数")
    cover_image: Optional[str] = Field(default=None, description="封面图片")
    dict_data: Optional[List[DictDataSimpleResponse]] = Field(default=None, description="字典数据")
    created_at: datetime = Field(description="创建时间")

    class Config:
        from_attributes = True


class ShopMergeResult(BaseModel):
    """店铺合并结果"""
    merged_shop_id: int = Field(description="合并后店铺ID")
    merged_shop_name: str = Field(description="合并后店铺名称")
    merged_count: int = Field(description="合并的店铺数量")


# 解决前向引用
CommentResponse.model_rebuild()