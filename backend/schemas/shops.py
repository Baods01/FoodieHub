from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============ 请求模型 ============

class ShopCreate(BaseModel):
    """创建店铺请求"""
    name: str = Field(min_length=1, max_length=100, description="店铺名称（必填）")
    description: Optional[str] = Field(default=None, max_length=2000, description="店铺描述（可选）")
    # 必填：字典数据编码列表，至少包含一个区域和一个品类
    dict_data_codes: List[str] = Field(
        ..., 
        description=(
            "字典数据编码列表（必填，至少包含一个区域和一个品类）\n"
            "品类编码：local_cuisine, hotpot, barbecue, western_food, "
            "snacks, specialty, drinks, desserts\n"
            "区域编码：nei_taisan, nei_huashan, nei_qilin, nei_liuyi, wai_outside"
        )
    )
    # 新增字段
    price_range: Optional[str] = Field(default=None, max_length=50, description="人均消费价格段，如 '30-50' 或 '50-100'")
    business_hours: Optional[str] = Field(default=None, max_length=50, description="营业时间，如 '08:00-22:00'")
    # 就餐方式：必填，至少选择一项
    dining_methods: List[str] = Field(
        ..., 
        description=(
            "就餐方式（必填，至少选择一项）\n"
            "- 'dine_in': 堂食\n"
            "- 'pickup': 自取\n"
            "- 'delivery': 外卖"
        )
    )
    address_detail: Optional[str] = Field(default=None, max_length=200, description="详细地址")
    tags: Optional[List[str]] = Field(default=None, description="店铺标签数组，如 ['环境好', '速度快']")
    menu_items: Optional[List["MenuItemCreateRequest"]] = Field(default=None, description="初始菜单项（可选）")


class MenuItemCreateRequest(BaseModel):
    """创建菜单项请求"""
    name: str = Field(min_length=1, max_length=100, description="菜品名称")
    price: Optional[Decimal] = Field(default=None, ge=0, description="价格")
    description: Optional[str] = Field(default=None, max_length=500, description="菜品描述")


class MenuItemAddRequest(BaseModel):
    """添加菜单项请求"""
    name: str = Field(..., min_length=1, max_length=100, description="菜品名称（必填）")
    price: Decimal = Field(..., gt=0, description="价格（必填，单位：元，必须大于0）")
    description: Optional[str] = Field(default=None, max_length=500, description="菜品描述（可选）")


class ShopUpdate(BaseModel):
    """更新店铺请求（管理员）"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="店铺名称")
    description: Optional[str] = Field(default=None, max_length=2000, description="店铺描述")
    is_active: Optional[bool] = Field(default=None, description="是否启用（软删除）")
    
    # 新增：区域编码列表
    location_codes: Optional[List[str]] = Field(
        default=None,
        description="区域编码列表（如：['nei_taisan', 'nei_huashan']）。不传则保持原区域不变"
    )
    # 新增：品类编码列表
    category_codes: Optional[List[str]] = Field(
        default=None,
        description="品类编码列表（如：['local_cuisine', 'hotpot']）。不传则保持原品类不变"
    )


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
    keyword: Optional[str] = Field(default=None, max_length=100, description="搜索关键词（店铺名称、描述）")
    category_codes: Optional[List[str]] = Field(default=None, description="品类筛选（编码列表，如 ['hotpot', 'snacks']）")
    district_codes: Optional[List[str]] = Field(default=None, description="区域筛选（编码列表，如 ['nei_taisan', 'nei_huashan']）")
    min_rating: Optional[float] = Field(default=None, ge=0, le=5, description="最低评分筛选")
    sort_by: str = Field(default="favorite_count", pattern="^(created_at|average_rating|view_count|favorite_count)$", description="排序字段")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="排序方向")
    page: int = Field(default=1, ge=1, description="页码（从1开始）")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


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
    rating_distribution: Optional[RatingDistribution] = Field(default=None, description="评分分布统计")
    aliases: Optional[List[str]] = Field(default=None, description="别名列表")
    merged_into_id: Optional[int] = Field(default=None, description="合并后店铺ID")
    # 新增字段
    price_range: Optional[str] = Field(default=None, description="人均消费价格段，如 '30-50' 或 '50-100'")
    business_hours: Optional[str] = Field(default=None, description="营业时间，如 '08:00-22:00'")
    dining_methods: Optional[List[str]] = Field(default=None, description="就餐方式：['dine_in', 'pickup', 'delivery']")
    address_detail: Optional[str] = Field(default=None, description="详细地址")
    tags: Optional[List[str]] = Field(default=None, description="店铺标签数组，如 ['环境好', '速度快']")
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
    is_favorited: bool = Field(default=False, description="当前用户是否已收藏")
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