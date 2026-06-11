from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============ 图片上传请求 ============

class ImageUploadRequest(BaseModel):
    """图片上传请求"""
    url: str = Field(..., description="图片访问路径")
    entity_type: str = Field(..., description="实体类型：shop / menu_item / shop_comment 等")
    entity_id: int = Field(..., description="实体ID")
    file_size: Optional[int] = Field(default=None, description="文件大小（字节）")
    width: Optional[int] = Field(default=None, description="图片宽度（像素）")
    height: Optional[int] = Field(default=None, description="图片高度（像素）")
    mime_type: Optional[str] = Field(default=None, description="MIME 类型")
    extra: Optional[dict] = Field(default=None, description="扩展信息")


# ============ 图片响应 ============

class ImageResponse(BaseModel):
    """图片响应"""
    id: int = Field(description="图片ID")
    url: str = Field(description="图片URL")
    entity_type: str = Field(description="关联实体类型")
    entity_id: int = Field(description="关联实体ID")
    file_size: Optional[int] = Field(default=None, description="文件大小（字节）")
    width: Optional[int] = Field(default=None, description="图片宽度（像素）")
    height: Optional[int] = Field(default=None, description="图片高度（像素）")
    mime_type: Optional[str] = Field(default=None, description="MIME 类型")
    extra: Optional[dict] = Field(default=None, description="扩展信息")
    uploader_id: Optional[int] = Field(default=None, description="上传者用户ID")
    created_at: datetime = Field(description="上传时间")

    class Config:
        from_attributes = True
