from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from schemas.common import ResponseModel
from schemas.users import UserResponse
from services import (
    UserService, ShopService, FeedbackService,
    MessageService, AnalyticsService,
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


@router.get("/users/{user_id}", response_model=ResponseModel, summary="用户详情（管理员）")
async def admin_get_user(
    user_id: int,
    current_user: UserResponse = Depends(require_admin),
):
    from models.users import Users
    user = await Users.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return ResponseModel.success(data=UserResponse.model_validate(user), message="获取成功")


@router.post("/users/{user_id}/ban", response_model=ResponseModel, summary="封禁用户")
async def ban_user(
    user_id: int,
    reason: str = Query(..., min_length=1),
    current_user: UserResponse = Depends(require_admin),
):
    ok = await UserService.ban_user(user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    await LogService.log(action="ban_user", operator=current_user.id, target_type="user", target_id=user_id, detail={"reason": reason})
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
    await LogService.log(action="unban_user", operator=current_user.id, target_type="user", target_id=user_id, detail={"reason": reason})
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
    await LogService.log(action="ban_shop", operator=current_user.id, target_type="shop", target_id=shop_id, detail={"reason": reason})
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
    await LogService.log(action="unban_shop", operator=current_user.id, target_type="shop", target_id=shop_id, detail={"reason": reason})
    return ResponseModel.success(data={"shop_id": shop_id, "status": "active"})


# ==================== 反馈工单管理（合并举报+勘误） ====================

@router.get("/feedbacks", response_model=ResponseModel, summary="反馈列表")
async def list_feedbacks(
    type: Optional[str] = Query(None, pattern="^(complaint|edit_request)$"),
    status: Optional[str] = Query(None, pattern="^(pending|approved|rejected)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_admin),
):
    data = await FeedbackService.list(type=type, status=status, page=page, page_size=page_size)
    return ResponseModel.success(data=data)


@router.post("/feedbacks/{feedback_id}/approve", response_model=ResponseModel, summary="通过反馈")
async def approve_feedback(
    feedback_id: int,
    current_user: UserResponse = Depends(require_admin),
):
    result = await FeedbackService.approve(feedback_id, current_user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="反馈不存在")
    await LogService.log(action="approve_feedback", operator=current_user.id, target_type="feedback", target_id=feedback_id, detail={"type": result.type})
    return ResponseModel.success(data=result, message="已通过")


@router.post("/feedbacks/{feedback_id}/reject", response_model=ResponseModel, summary="驳回反馈")
async def reject_feedback(
    feedback_id: int,
    current_user: UserResponse = Depends(require_admin),
):
    result = await FeedbackService.reject(feedback_id, current_user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="反馈不存在")
    await LogService.log(action="reject_feedback", operator=current_user.id, target_type="feedback", target_id=feedback_id, detail={"type": result.type})
    return ResponseModel.success(data=result, message="已驳回")


# ==================== 店铺合并 ====================

@router.post("/shops/merge", response_model=ResponseModel, summary="合并店铺（管理员直接操作）")
async def merge_shops(
    main_shop_id: int = Query(...),
    duplicate_shop_ids: str = Query(..., description="从属店铺ID列表，逗号分隔如 '2,3'"),
    current_user: UserResponse = Depends(require_admin),
):
    try:
        ids = [int(x.strip()) for x in duplicate_shop_ids.split(",") if x.strip()]
        result = await ShopService.merge_shops(main_shop_id, ids)
        await LogService.log(action="merge_shops", operator=current_user.id, target_type="shop", target_id=main_shop_id, detail={"duplicate_ids": ids})
        return ResponseModel.success(data=result, message="合并成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))




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


# ==================== 店铺管理（管理员专用） ====================

@router.get("/shops", response_model=ResponseModel, summary="店铺列表（含被封禁）")
async def admin_list_shops(
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_admin),
):
    from models.shops import Shops
    from dao.image_dao import ImageDAO
    from dao.dict_dao import DictRelDAO
    from schemas.shops import ShopListItem

    qs = Shops.all()
    if keyword:
        qs = qs.filter(name__icontains=keyword)
    total = await qs.count()
    shops = await qs.order_by("-created_at").offset((page-1)*page_size).limit(page_size).all()

    items = []
    for s in shops:
        cover = await ImageDAO.get_first_by_entity("shop", s.id)
        tags = await DictRelDAO.get_entity_dicts("shop", s.id)
        dict_data = [{"id": t["dict_data_id"], "name": t["dict_data_name"], "dict_type_name": t["dict_type_name"]} for t in tags]
        items.append(ShopListItem(
            id=s.id, name=s.name, dict_data=dict_data,
            average_rating=s.average_rating, view_count=s.view_count,
            favorite_count=s.favorite_count, comment_count=s.comment_count,
            cover_image=cover.url if cover else None,
            is_favorited=False, is_banned=s.is_banned, is_active=s.is_active,
            created_at=s.created_at,
        ))
    return ResponseModel.success(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.get("/shops/{shop_id}", response_model=ResponseModel, summary="店铺详情（管理员）")
async def admin_get_shop(
    shop_id: int,
    current_user: UserResponse = Depends(require_admin),
):
    from dao.shops_dao import ShopsDAO
    from dao.dict_dao import DictRelDAO
    from dao.image_dao import ImageDAO
    from services.shop_service import ShopService
    shop = await ShopsDAO.get_by_id(shop_id, include_inactive=True)
    if not shop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="店铺不存在")
    result = await ShopService._build_detail(shop, is_fav=False, user_rating=None)
    return ResponseModel.success(data=result)


# ==================== 公告 ====================

@router.get("/announcements", response_model=ResponseModel, summary="公告列表")
async def list_announcements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_admin),
):
    from tortoise.functions import Count, Max
    from models.users import Messages

    qs = Messages.filter(type="announcement", is_active=True)
    # 统计去重后的公告总数
    all_titles = await qs.values_list("title", "content")
    total = len(set((t, c) for t, c in all_titles))

    # 按 title+content 去重，取最新时间，统计推送人数
    results = await qs.annotate(
        sent_count=Count("id"),
        latest_time=Max("created_at"),
    ).group_by("title", "content") \
     .order_by("-latest_time") \
     .offset((page - 1) * page_size) \
     .limit(page_size) \
     .values("title", "content", "sent_count", "latest_time")

    items = []
    for r in results:
        items.append({
            "title": r["title"],
            "content": r["content"],
            "sent_count": r["sent_count"],
            "created_at": r["latest_time"].isoformat(),
        })

    return ResponseModel.success(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.post("/announcements", response_model=ResponseModel, summary="发布公告")
async def create_announcement(
    title: str = Query(..., min_length=1),
    content: str = Query(..., min_length=1),
    current_user: UserResponse = Depends(require_admin),
):
    sent = await MessageService.send_announcement(title, content, sender_id=current_user.id)
    await LogService.log(action="publish_announcement", operator=current_user.id, target_type="announcement", target_id=0)
    return ResponseModel.success(data={"sent_count": sent}, message="公告发布成功")
