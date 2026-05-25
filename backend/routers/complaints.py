from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from schemas.complaints import (
    ComplaintCreateRequest, ComplaintResponse,
    ComplaintListResponse, ComplaintHandlerResponse,
    ComplaintStatsResponse, ComplaintHandleRequest
)
from schemas.common import ResponseModel
from schemas.users import UserResponse
from services.complaint_service import ComplaintService
from dependencies.auth import get_current_user, require_login, require_admin

router = APIRouter(prefix="/complaints")


@router.post(
    "/",
    response_model=ResponseModel[ComplaintResponse],
    summary="发起举报"
)
async def create_complaint(
    request: ComplaintCreateRequest,
    current_user: UserResponse = Depends(require_login)
):
    """
    发起举报（普通用户）
    
    **功能描述**：用户可针对平台上的评论、店铺或图片三种内容实体发起举报。
    
    **请求参数**：
    - `complainant_type`: 被举报内容类型（comment/shop/image）
    - `complainant_id`: 被举报内容ID
    - `reason_code`: 举报原因编码（来自预设字典）
    - `description`: 补充说明（可选）
    
    **预设举报原因编码（8个）**：
    - `advertisement`: 广告营销（包含商业广告、推广引流等内容）
    - `personal_attack`: 人身攻击（包含辱骂、诽谤、恶意攻击等内容）
    - `false_info`: 信息不实（店铺信息、评论内容等与事实不符）
    - `inappropriate_image`: 图片违规（包含无关广告图、令人不适的图片）
    - `spam`: 恶意刷屏（重复发布相同内容或无意义内容）
    - `rumor`: 造谣恶评（故意发布虚假负面信息进行抹黑）
    - `privacy`: 涉及隐私（泄露他人隐私信息）
    - `other`: 其他（其他违反社区规范的行为）
    
    **业务规则**：
    - 同一用户对同一内容实体的同一类型举报仅允许一条未处理记录
    - 举报原因编码需从预设字典中选择
    
    **错误码**：
    - 400: 已存在未处理的重复举报或无效参数
    - 404: 被举报内容不存在
    """
    complaint = await ComplaintService.create_complaint(current_user.id, request)
    return ResponseModel.success(data=complaint, message="举报提交成功")


@router.get(
    "/{complaint_id}",
    response_model=ResponseModel[ComplaintResponse],
    summary="查看举报详情"
)
async def get_complaint_detail(
    complaint_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    查看举报详情
    
    **功能描述**：用户可查看自己发起的举报详情，管理员可查看所有举报详情。
    
    **路径参数**：
    - `complaint_id`: 举报ID
    
    **错误码**：
    - 404: 举报记录不存在
    """
    complaint = await ComplaintService.get_complaint_by_id(complaint_id)
    return ResponseModel.success(data=complaint, message="获取成功")


@router.get(
    "/",
    response_model=ResponseModel[ComplaintListResponse],
    summary="获取我的举报列表"
)
async def get_my_complaints(
    status: Optional[str] = Query(None, description="状态过滤：pending/approved/rejected"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    获取我的举报列表（普通用户）
    
    **功能描述**：用户可查看自己发起的所有举报记录。
    
    **查询参数**：
    - `status`: 状态过滤（可选）
    - `page`: 页码
    - `page_size`: 每页数量
    
    **返回内容**：
    - 举报列表（按时间倒序）
    - 分页信息
    """
    complaints = await ComplaintService.get_user_complaints(
        user_id=current_user.id,
        status=status,
        page=page,
        page_size=page_size
    )
    return ResponseModel.success(data=complaints, message="获取成功")


@router.get(
    "/admin/pending",
    response_model=ResponseModel[ComplaintListResponse],
    summary="获取待处理举报列表（管理员）"
)
async def get_pending_complaints(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: UserResponse = Depends(require_admin)
):
    """
    获取待处理举报列表（管理员）
    
    **功能描述**：管理员可查看所有待处理的举报记录。
    
    **查询参数**：
    - `page`: 页码
    - `page_size`: 每页数量
    
    **权限要求**：管理员权限
    
    **返回内容**：
    - 待处理举报列表（按时间倒序）
    - 分页信息
    """
    complaints = await ComplaintService.get_pending_complaints(page=page, page_size=page_size)
    return ResponseModel.success(data=complaints, message="获取成功")


@router.post(
    "/{complaint_id}/handle",
    response_model=ResponseModel[ComplaintResponse],
    summary="处理举报（管理员）"
)
async def handle_complaint(
    complaint_id: int,
    request: ComplaintHandleRequest,
    current_user: UserResponse = Depends(require_admin)
):
    """
    处理举报（管理员）
    
    **功能描述**：管理员处理用户举报，执行相应的处置操作。
    
    **路径参数**：
    - `complaint_id`: 举报ID
    
    **请求参数**：
    - `action`: 处理动作（delete_comment/ban_shop/remove_image/dismiss）
    - `result_description`: 处理结果描述（可选）
    
    **权限要求**：管理员权限
    
    **业务规则**：
    - delete_comment: 删除评论
    - ban_shop: 封禁店铺
    - remove_image: 移除图片
    - dismiss: 驳回举报
    
    **错误码**：
    - 403: 无管理员权限
    - 404: 举报记录不存在
    - 400: 举报已被处理或无效操作
    """
    complaint = await ComplaintService.handle_complaint(
        complaint_id=complaint_id,
        handler_id=current_user.id,
        request=request
    )
    return ResponseModel.success(data=complaint, message="处理成功")


@router.get(
    "/admin/stats",
    response_model=ResponseModel[ComplaintStatsResponse],
    summary="获取举报统计（管理员）"
)
async def get_complaint_stats(
    current_user: UserResponse = Depends(require_admin)
):
    """
    获取举报统计（管理员）
    
    **功能描述**：管理员查看平台举报统计信息。
    
    **权限要求**：管理员权限
    
    **返回内容**：
    - pending: 待处理数量
    - approved: 已批准数量
    - rejected: 已驳回数量
    - total: 总数量
    """
    stats = await ComplaintService.get_complaint_stats()
    return ResponseModel.success(data=stats, message="获取成功")


@router.get(
    "/{complaint_id}/handlers",
    response_model=ResponseModel[List[ComplaintHandlerResponse]],
    summary="获取举报处理记录"
)
async def get_complaint_handlers(
    complaint_id: int,
    current_user: UserResponse = Depends(require_login)
):
    """
    获取举报处理记录
    
    **功能描述**：查看举报的处理历史记录。
    
    **路径参数**：
    - `complaint_id`: 举报ID
    
    **权限要求**：管理员或举报发起者
    
    **返回内容**：
    - 处理记录列表（按时间顺序）
    
    **错误码**：
    - 403: 无权限访问
    - 404: 举报记录不存在
    """
    # 检查权限：管理员或举报发起者
    complaint = await ComplaintService.get_complaint_by_id(complaint_id)
    
    # 只有管理员或举报发起者可以查看
    if current_user.role != 1 and current_user.id != complaint.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问此举报处理记录"
        )
    
    handlers = await ComplaintService.get_complaint_handlers(complaint_id)
    return ResponseModel.success(data=handlers, message="获取成功")
