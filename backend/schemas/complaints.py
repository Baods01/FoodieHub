from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ComplaintCreateRequest(BaseModel):
    """
    举报创建请求模型
    """
    complainant_type: str = Field(
        ..., 
        description="被举报内容类型：comment（评论）、shop（店铺）、image（图片）",
        pattern="^(comment|shop|image)$"
    )
    complainant_id: int = Field(..., description="被举报内容ID", ge=1)
    reason_code: str = Field(
        ..., 
        description="举报原因编码（来自预设字典）",
        max_length=50
    )
    description: Optional[str] = Field(None, description="补充说明", max_length=500)


class ComplaintResponse(BaseModel):
    """
    举报响应模型
    """
    id: int = Field(..., description="举报唯一标识")
    complainant_type: str = Field(..., description="被举报内容类型")
    complainant_id: int = Field(..., description="被举报内容ID")
    reason_code: str = Field(..., description="举报原因编码")
    reason_name: Optional[str] = Field(None, description="举报原因名称")
    description: Optional[str] = Field(None, description="补充说明")
    status: str = Field(..., description="处理状态：pending、approved、rejected")
    user_id: int = Field(..., description="举报发起用户ID")
    user_nickname: Optional[str] = Field(None, description="举报发起用户昵称")
    created_at: datetime = Field(..., description="举报时间")
    updated_at: datetime = Field(..., description="更新时间")


class ComplaintListResponse(BaseModel):
    """
    举报列表响应模型
    """
    complaints: List[ComplaintResponse] = Field(..., description="举报列表")
    total: int = Field(..., description="举报总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class ComplaintHandlerResponse(BaseModel):
    """
    举报处理记录响应模型
    """
    id: int = Field(..., description="处理记录唯一标识")
    complaint_id: int = Field(..., description="关联的举报ID")
    handler_id: Optional[int] = Field(None, description="处理管理员ID")
    handler_nickname: Optional[str] = Field(None, description="处理管理员昵称")
    action: str = Field(..., description="处理动作")
    result_description: Optional[str] = Field(None, description="处理结果描述")
    created_at: datetime = Field(..., description="处理时间")


class ComplaintStatsResponse(BaseModel):
    """
    举报统计响应模型
    """
    pending: int = Field(..., description="待处理数量")
    approved: int = Field(..., description="已批准数量")
    rejected: int = Field(..., description="已驳回数量")
    total: int = Field(..., description="总数量")


class ComplaintHandleRequest(BaseModel):
    """
    举报处理请求模型（管理员用）
    """
    action: str = Field(
        ..., 
        description="处理动作：delete_comment、ban_shop、remove_image、dismiss",
        pattern="^(delete_comment|ban_shop|remove_image|dismiss)$"
    )
    result_description: Optional[str] = Field(None, description="处理结果描述")
