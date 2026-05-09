from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ 图片上传请求 ============

class ImageUploadRequest(BaseModel):
    """图片上传请求"""
    entity_type: str = Field(..., description="实体类型：shop 或 menu_item")
    entity_id: int = Field(..., description="实体ID")
    url: str = Field(..., description="图片访问路径")
    extra: Optional[dict] = Field(default=None, description="扩展信息（如宽高、文件大小等）")


class MenuItemWithImageRequest(BaseModel):
    """带图片的菜单项请求"""
    name: str = Field(..., min_length=1, max_length=100, description="菜品名称（必填）")
    price: Optional[float] = Field(default=None, ge=0, description="价格（必填）")
    description: Optional[str] = Field(default=None, max_length=500, description="菜品描述（可选）")


# ============ 图片响应 ============

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


class MenuItemImageResponse(BaseModel):
    """菜单项图片响应"""
    id: int = Field(description="菜单项ID")
    name: str = Field(description="菜品名称")
    price: Optional[float] = Field(default=None, description="价格")
    description: Optional[str] = Field(default=None, description="菜品描述")
    image_url: Optional[str] = Field(default=None, description="菜品图片URL")
    created_at: datetime = Field(description="创建时间")

    class Config:
        from_attributes = True