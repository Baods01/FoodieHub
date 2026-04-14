from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============ 请求模型 ============

class DictTypeCreate(BaseModel):
    """创建字典类型请求"""
    code: str = Field(min_length=1, max_length=50, description="类型编码")
    name: str = Field(min_length=1, max_length=50, description="类型名称")
    target_table: str = Field(min_length=1, max_length=50, description="目标表名")
    description: Optional[str] = Field(default=None, max_length=255, description="类型描述")
    sort_order: int = Field(default=0, description="排序顺序")


class DictTypeUpdate(BaseModel):
    """更新字典类型请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50, description="类型名称")
    target_table: Optional[str] = Field(default=None, min_length=1, max_length=50, description="目标表名")
    description: Optional[str] = Field(default=None, max_length=255, description="类型描述")
    sort_order: Optional[int] = Field(default=None, description="排序顺序")


class DictDataCreate(BaseModel):
    """创建字典数据请求"""
    dict_type_id: int = Field(description="所属字典类型ID")
    code: str = Field(min_length=1, max_length=50, description="数据编码")
    name: str = Field(min_length=1, max_length=50, description="显示名称")
    value: Optional[str] = Field(default=None, max_length=255, description="额外值")
    sort_order: int = Field(default=0, description="排序顺序")
    is_default: bool = Field(default=False, description="是否为默认值")
    extra: Optional[dict] = Field(default=None, description="扩展字段")


class DictDataUpdate(BaseModel):
    """更新字典数据请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50, description="显示名称")
    value: Optional[str] = Field(default=None, max_length=255, description="额外值")
    sort_order: Optional[int] = Field(default=None, description="排序顺序")
    is_default: Optional[bool] = Field(default=None, description="是否为默认值")
    extra: Optional[dict] = Field(default=None, description="扩展字段")


# ============ 响应模型 ============

class DictTypeResponse(BaseModel):
    """字典类型响应"""
    id: int = Field(description="类型ID")
    code: str = Field(description="类型编码")
    name: str = Field(description="类型名称")
    target_table: str = Field(description="目标表名")
    description: Optional[str] = Field(default=None, description="类型描述")
    sort_order: int = Field(description="排序顺序")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


class DictDataResponse(BaseModel):
    """字典数据响应"""
    id: int = Field(description="数据ID")
    dict_type_id: int = Field(description="所属字典类型ID")
    dict_type: Optional[DictTypeResponse] = Field(default=None, description="所属字典类型")
    code: str = Field(description="数据编码")
    name: str = Field(description="显示名称")
    value: Optional[str] = Field(default=None, description="额外值")
    sort_order: int = Field(description="排序顺序")
    is_default: bool = Field(description="是否为默认值")
    extra: Optional[dict] = Field(default=None, description="扩展字段")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


class DictTypeWithChildrenResponse(DictTypeResponse):
    """字典类型响应（含子数据）"""
    children: list[DictDataResponse] = Field(default=[], description="字典数据列表")