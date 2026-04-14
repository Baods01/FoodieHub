from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .users import UserResponse
from .shops import ShopListItem


# ============ 请求模型 ============

class ShopEditRequestCreate(BaseModel):
    """提交店铺信息修改申请请求"""
    proposed_data: dict = Field(description="提议修改的字段及新值，JSON格式")


class ShopEditRequestApprove(BaseModel):
    """审核通过请求"""
    remark: Optional[str] = Field(default=None, max_length=255, description="审核备注")


class ShopEditRequestReject(BaseModel):
    """审核拒绝请求"""
    reason: str = Field(min_length=1, max_length=500, description="拒绝原因")


class ShopEditRequestListRequest(BaseModel):
    """编辑申请列表查询请求"""
    status: Optional[str] = Field(default=None, pattern="^(pending|approved|rejected)$", description="状态筛选")
    shop_name: Optional[str] = Field(default=None, max_length=100, description="店铺名称模糊搜索")
    user_id: Optional[int] = Field(default=None, description="申请人ID筛选")


# ============ 响应模型 ============

class ProposedDataResponse(BaseModel):
    """提议修改的数据响应"""
    field_name: str = Field(description="字段名称")
    old_value: Optional[str] = Field(default=None, description="原值")
    new_value: Optional[str] = Field(default=None, description="新值")


class ShopEditRequestResponse(BaseModel):
    """店铺编辑申请响应"""
    id: int = Field(description="申请ID")
    shop_id: int = Field(description="店铺ID")
    shop: Optional[ShopListItem] = Field(default=None, description="店铺信息")
    user: UserResponse = Field(description="申请用户")
    proposed_data: dict = Field(description="提议修改的字段及新值")
    status: str = Field(description="状态：pending、approved、rejected")
    admin: Optional[UserResponse] = Field(default=None, description="审核管理员")
    remark: Optional[str] = Field(default=None, description="审核备注")
    created_at: datetime = Field(description="申请时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


class EditRequestStats(BaseModel):
    """编辑申请统计"""
    pending_count: int = Field(default=0, description="待审核数量")
    approved_count: int = Field(default=0, description="已通过数量")
    rejected_count: int = Field(default=0, description="已拒绝数量")
    total_count: int = Field(default=0, description="总数量")