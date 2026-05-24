from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AdminLogQueryParams(BaseModel):
    """
    管理员日志查询参数
    """
    operator_id: Optional[int] = Field(None, description="操作人ID")
    operation_module: Optional[str] = Field(None, description="操作模块")
    operation_type: Optional[str] = Field(None, description="操作类型")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    target_object_type: Optional[str] = Field(None, description="目标对象类型")
    target_object_id: Optional[int] = Field(None, description="目标对象ID")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页大小")


class AdminLogBase(BaseModel):
    """
    管理员日志基础模型
    """
    id: int
    operator_id: int
    operator_account: str
    operation_time: datetime
    operation_ip: str
    operation_type: str
    operation_module: str
    target_object_id: Optional[int]
    target_object_type: Optional[str]
    before_snapshot: Optional[dict]
    after_snapshot: Optional[dict]
    operation_result: str
    operation_description: Optional[str]
    created_at: datetime
    updated_at: datetime


class AdminLogResponse(BaseModel):
    """
    管理员日志响应模型
    """
    items: List[AdminLogBase]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminLogExportResponse(BaseModel):
    """
    管理员日志导出响应模型
    """
    id: int
    operator_id: int
    operator_account: str
    operation_time: str
    operation_ip: str
    operation_type: str
    operation_module: str
    target_object_id: Optional[int]
    target_object_type: Optional[str]
    before_snapshot: Optional[dict]
    after_snapshot: Optional[dict]
    operation_result: str
    operation_description: Optional[str]
    created_at: str
    updated_at: str