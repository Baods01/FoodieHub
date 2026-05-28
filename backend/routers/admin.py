from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from schemas.common import ResponseModel
from schemas.users import UserResponse
from services import (
    UserService, ShopService, ComplaintService,
    GovernanceService, MessageService, AnalyticsService,
    LogService,
)
from utils.auth import require_admin

router = APIRouter(prefix="/admin", tags=["管理员模块"])


# ==================== 仪表盘 ====================

@router.get("/overview", response_model=ResponseModel, summary="平台概览")
async def get_overview(current_user: UserResponse = Depends(require_admin)):
    data = await AnalyticsService.get_overview()
    return ResponseModel.success(data=data)


@router.get("/daily-trends", response_model=ResponseModel, summary="每日趋势")
async def get_daily_trends(
    days: int = Query(7, ge=1, le=30),
    current_user: UserResponse = Depends(require_admin),
):
    data = await AnalyticsService.get_daily_trends(days=days)
    return ResponseModel.success(data=data)


@router.get("/pending-counts", response_model=ResponseModel, summary="待处理工单")
async def get_pending_counts(current_user: UserResponse = Depends(require_admin)):
    data = await AnalyticsService.get_pending_counts()
    return ResponseModel.success(data=data)


# ==================== 用户管理 ====================

@router.get("/users", response_model=ResponseModel, summary="用户列表")
async def list_users(
    is_active: Optional[bool] = Query(None),
    is_banned: Optional[bool] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_admin),
):
    data = await UserService.list(
        is_active=is_active, is_banned=is_banned,
        keyword=keyword, page=page, page_size=page_size,
    )
    return ResponseModel.success(data=data)


@router.post("/users/{user_id}/ban", response_model=ResponseModel, summary="封禁用户")
async def ban_user(
    user_id: int,
    reason: str = Query(..., min_length=1),
    current_user: UserResponse = Depends(require_admin),
):
    ok = await UserService.ban_user(user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    await LogService.log(action="ban_user", operator=current_user, target_type="user", target_id=user_id, detail={"reason": reason})
    return ResponseModel.success(data={"user_id": user_id, "status": "banned"})


@router.post("/users/{user_id}/unban", response_model=ResponseModel, summary="解封用户")
async def unban_user(
    user_id: int,
    reason: Optional[str] = Query(None),
    current_user: UserResponse = Depends(require_admin),
):
    ok = await UserService.unban_user(user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    await LogService.log(action="unban_user", operator=current_user, target_type="user", target_id=user_id, detail={"reason": reason})
    return ResponseModel.success(data={"user_id": user_id, "status": "active"})


# ==================== 店铺管理 ====================

@router.post("/shops/{shop_id}/ban", response_model=ResponseModel, summary="封禁店铺")
async def ban_shop(
    shop_id: int,
    reason: str = Query(..., min_length=1),
    current_user: UserResponse = Depends(require_admin),
):
    ok = await ShopService.ban_shop(shop_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="店铺不存在")
    await LogService.log(action="ban_shop", operator=current_user, target_type="shop", target_id=shop_id, detail={"reason": reason})
    return ResponseModel.success(data={"shop_id": shop_id, "status": "banned"})


@router.post("/shops/{shop_id}/unban", response_model=ResponseModel, summary="解封店铺")
async def unban_shop(
    shop_id: int,
    reason: Optional[str] = Query(None),
    current_user: UserResponse = Depends(require_admin),
):
    ok = await ShopService.unban_shop(shop_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="店铺不存在")
    await LogService.log(action="unban_shop", operator=current_user, target_type="shop", target_id=shop_id, detail={"reason": reason})
    return ResponseModel.success(data={"shop_id": shop_id, "status": "active"})


# ==================== 举报管理 ====================

@router.get("/complaints", response_model=ResponseModel, summary="举报列表")
async def list_complaints(
    status: Optional[str] = Query(None, pattern="^(pending|approved|rejected)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_admin),
):
    data = await ComplaintService.list(status=status, page=page, page_size=page_size)
    return ResponseModel.success(data=data.model_dump())


@router.post("/complaints/{complaint_id}/approve", response_model=ResponseModel, summary="通过举报")
async def approve_complaint(
    complaint_id: int,
    action: str = Query(..., pattern="^(delete_comment|ban_shop|remove_image|dismiss)$"),
    result_description: Optional[str] = Query(None),
    current_user: UserResponse = Depends(require_admin),
):
    result = await ComplaintService.approve(complaint_id, current_user.id, action, result_description)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="举报不存在")
    return ResponseModel.success(data=result.model_dump())


@router.post("/complaints/{complaint_id}/reject", response_model=ResponseModel, summary="驳回举报")
async def reject_complaint(
    complaint_id: int,
    result_description: Optional[str] = Query(None),
    current_user: UserResponse = Depends(require_admin),
):
    result = await ComplaintService.reject(complaint_id, current_user.id, result_description)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="举报不存在")
    return ResponseModel.success(data=result.model_dump())


# ==================== 勘误管理 ====================

@router.get("/edit-requests", response_model=ResponseModel, summary="勘误列表")
async def list_edit_requests(
    status: Optional[str] = Query(None, pattern="^(pending|approved|rejected)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_admin),
):
    data = await GovernanceService.list_edit_requests(status=status, page=page, page_size=page_size)
    return ResponseModel.success(data=data.model_dump())


@router.post("/edit-requests/{request_id}/approve", response_model=ResponseModel, summary="通过勘误")
async def approve_edit_request(
    request_id: int,
    current_user: UserResponse = Depends(require_admin),
):
    result = await GovernanceService.approve_edit_request(request_id, current_user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申请不存在")
    return ResponseModel.success(data=result.model_dump())


@router.post("/edit-requests/{request_id}/reject", response_model=ResponseModel, summary="驳回勘误")
async def reject_edit_request(
    request_id: int,
    current_user: UserResponse = Depends(require_admin),
):
    result = await GovernanceService.reject_edit_request(request_id, current_user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申请不存在")
    return ResponseModel.success(data=result.model_dump())


# ==================== 日志 ====================

@router.get("/logs", response_model=ResponseModel, summary="操作日志")
async def list_logs(
    action: Optional[str] = Query(None),
    target_type: Optional[str] = Query(None),
    operator_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_admin),
):
    data = await LogService.get_logs(
        action=action, target_type=target_type,
        operator_id=operator_id, page=page, page_size=page_size,
    )
    return ResponseModel.success(data=data)


# ==================== 公告 ====================

@router.post("/announcements", response_model=ResponseModel, summary="发布公告")
async def create_announcement(
    title: str = Query(..., min_length=1),
    content: str = Query(..., min_length=1),
    current_user: UserResponse = Depends(require_admin),
):
    sent = await MessageService.send_announcement(title, content, sender_id=current_user.id)
    await LogService.log(action="publish_announcement", operator=current_user, target_type="announcement", target_id=0)
    return ResponseModel.success(data={"sent_count": sent}, message="公告发布成功")
