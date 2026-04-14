from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Optional, List
from datetime import datetime

T = TypeVar("T")


class PaginationRequest(BaseModel):
    """分页请求参数"""
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量，最大100")


class PaginationMeta(BaseModel):
    """分页元数据"""
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")


class PaginationResponse(BaseModel, Generic[T]):
    """分页响应数据"""
    items: List[T] = Field(default=[], description="数据列表")
    meta: PaginationMeta = Field(description="分页信息")


class ResponseModel(BaseModel, Generic[T]):
    """统一 API 响应模型"""
    code: int = Field(default=200, description="状态码：200成功，其他失败")
    message: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")

    @classmethod
    def success(cls, data: T = None, message: str = "success") -> "ResponseModel[T]":
        """成功响应"""
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int = 400, message: str = "请求失败") -> "ResponseModel[T]":
        """错误响应"""
        return cls(code=code, message=message, data=None)


# 分页成功响应快捷方法
def paginated_success(
    items: list,
    total: int,
    page: int = 1,
    page_size: int = 20,
    message: str = "success"
) -> ResponseModel[PaginationResponse[T]]:
    """分页成功响应"""
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return ResponseModel.success(
        data=PaginationResponse(
            items=items,
            meta=PaginationMeta(
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
        ),
        message=message
    )