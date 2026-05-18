from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from schemas.common import ResponseModel
from schemas.users import UserResponse
from schemas.shops import ShopResponse
from schemas.complaints import ComplaintResponse, ComplaintListResponse, ComplaintStatsResponse
from models.users import Users
from models.shops import Shops, Comments
from models.complaints import Complaints
from dao.message_dao import MessageDAO
from dao.ban_dao import BanDAO
from services.user_service import UserService
from dependencies.auth import require_admin
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["管理员模块"])


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int = Field(description="用户总数")
    users: List[UserResponse] = Field(description="用户列表")


class PlatformStatsResponse(BaseModel):
    """平台统计数据响应"""
    total_shops: int = Field(description="店铺总数")
    total_users: int = Field(description="用户总数")
    total_comments: int = Field(description="评论总数")
    active_shops_7d: int = Field(description="近7日新增店铺")
    active_users_7d: int = Field(description="近7日新增用户")
    active_comments_7d: int = Field(description="近7日新增评论")
    daily_stats: List[dict] = Field(description="近7日每日新增趋势")


class DailyStatsItem(BaseModel):
    """每日统计数据项"""
    date: str = Field(description="日期")
    new_shops: int = Field(description="新增店铺数")
    new_users: int = Field(description="新增用户数")
    new_comments: int = Field(description="新增评论数")


# ==================== FD06-04 封禁/解封店铺 ====================

@router.post(
    "/shops/{shop_id}/ban",
    response_model=ResponseModel[dict],
    summary="封禁店铺（管理员）"
)
async def ban_shop(
    shop_id: int,
    reason: str = Query(..., min_length=1, max_length=255, description="封禁原因（必填）"),
    current_user: UserResponse = Depends(require_admin)
):
    """
    封禁店铺（管理员）

    **功能描述**：管理员对存在严重问题的店铺执行封禁操作。

    **路径参数**：
    - `shop_id`: 店铺ID

    **查询参数**：
    - `reason`: 封禁原因（必填，最多255字符）

    **业务规则**：
    - 封禁后店铺全局隐藏且不可被搜索与浏览
    - 数据库不删除数据，仅更新状态标记（is_active=False）
    - 在bans表插入封禁记录
    - 封禁操作记录在 user_behavior_logs

    **错误码**：
    - 403: 无管理员权限
    - 404: 店铺不存在
    - 400: 店铺已被封禁或未填写封禁原因
    """
    shop = await Shops.get_or_none(id=shop_id)

    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="店铺不存在"
        )

    if not shop.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="店铺已被封禁"
        )

    if not reason or not reason.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请填写封禁原因"
        )

    # 1. 插入封禁记录到bans表
    await BanDAO.create_ban_record(
        target_type="shop",
        target_id=shop_id,
        reason=reason,
        banned_by=current_user.id
    )

    # 2. 更新店铺状态
    shop.is_active = False
    await shop.save()

    # 3. 记录行为日志
    await UserService.log_user_behavior(
        user_id=current_user.id,
        behavior_type="ban_shop",
        target_type="shop",
        target_id=shop_id
    )

    return ResponseModel.success(data={"shop_id": shop_id, "status": "banned"}, message="店铺已封禁")


@router.post(
    "/shops/{shop_id}/unban",
    response_model=ResponseModel[dict],
    summary="解封店铺（管理员）"
)
async def unban_shop(
    shop_id: int,
    reason: Optional[str] = Query(None, description="解封原因"),
    current_user: UserResponse = Depends(require_admin)
):
    """
    解封店铺（管理员）

    **功能描述**：管理员对已封禁的店铺执行解封操作，恢复其显示。

    **路径参数**：
    - `shop_id`: 店铺ID

    **查询参数**：
    - `reason`: 解封原因（可选）

    **业务规则**：
    - 解封后店铺恢复正常显示
    - 更新bans表中的封禁记录
    - 封禁操作记录在 user_behavior_logs

    **错误码**：
    - 403: 无管理员权限
    - 404: 店铺不存在
    - 400: 店铺未被封禁
    """
    shop = await Shops.get_or_none(id=shop_id)

    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="店铺不存在"
        )

    if shop.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="店铺未被封禁"
        )

    # 1. 更新bans表中的封禁记录
    await BanDAO.unban(
        target_type="shop",
        target_id=shop_id,
        unbanned_by=current_user.id,
        unban_reason=reason
    )

    # 2. 更新店铺状态
    shop.is_active = True
    await shop.save()

    # 3. 记录行为日志
    await UserService.log_user_behavior(
        user_id=current_user.id,
        behavior_type="unban_shop",
        target_type="shop",
        target_id=shop_id
    )

    return ResponseModel.success(data={"shop_id": shop_id, "status": "active"}, message="店铺已解封")


# ==================== FD06-05 封禁/解封用户 ====================

@router.post(
    "/users/{user_id}/ban",
    response_model=ResponseModel[dict],
    summary="封禁用户（管理员）"
)
async def ban_user(
    user_id: int,
    reason: str = Query(..., min_length=1, max_length=255, description="封禁原因（必填）"),
    current_user: UserResponse = Depends(require_admin)
):
    """
    封禁用户（管理员）

    **功能描述**：管理员对严重违规用户执行封禁操作。

    **路径参数**：
    - `user_id`: 用户ID

    **查询参数**：
    - `reason`: 封禁原因（必填，最多255字符）

    **业务规则**：
    - 封禁后冻结用户全部操作权限（读写全部冻结），用户无法登录系统
    - 数据库不删除用户数据，仅更新状态标记（is_active=False）
    - 在bans表插入封禁记录
    - 封禁操作记录在 user_behavior_logs

    **错误码**：
    - 403: 无管理员权限
    - 404: 用户不存在
    - 400: 用户已被封禁、不能封禁管理员或未填写封禁原因
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能封禁自己"
        )

    user = await Users.get_or_none(id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if user.role == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能封禁管理员"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被封禁"
        )

    if not reason or not reason.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请填写封禁原因"
        )

    # 1. 插入封禁记录到bans表
    await BanDAO.create_ban_record(
        target_type="user",
        target_id=user_id,
        reason=reason,
        banned_by=current_user.id
    )

    # 2. 更新用户状态
    user.is_active = False
    await user.save()

    # 3. 记录行为日志
    await UserService.log_user_behavior(
        user_id=current_user.id,
        behavior_type="ban_user",
        target_type="user",
        target_id=user_id
    )

    return ResponseModel.success(
        data={"user_id": user_id, "is_active": False, "status": "已封禁"},
        message="用户已封禁（冻结全部操作权限）"
    )


@router.post(
    "/users/{user_id}/unban",
    response_model=ResponseModel[dict],
    summary="解封用户（管理员）"
)
async def unban_user(
    user_id: int,
    reason: Optional[str] = Query(None, description="解封原因"),
    current_user: UserResponse = Depends(require_admin)
):
    """
    解封用户（管理员）

    **功能描述**：管理员对已封禁的用户执行解封操作，恢复其权限。

    **路径参数**：
    - `user_id`: 用户ID

    **查询参数**：
    - `reason`: 解封原因（可选）

    **业务规则**：
    - 解封后用户恢复正常状态（is_active=True）
    - 更新bans表中的封禁记录
    - 封禁操作记录在 user_behavior_logs

    **错误码**：
    - 403: 无管理员权限
    - 404: 用户不存在
    - 400: 用户未被封禁
    """
    user = await Users.get_or_none(id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未被封禁"
        )

    # 1. 更新bans表中的封禁记录
    await BanDAO.unban(
        target_type="user",
        target_id=user_id,
        unbanned_by=current_user.id,
        unban_reason=reason
    )

    # 2. 更新用户状态
    user.is_active = True
    await user.save()

    # 3. 记录行为日志
    await UserService.log_user_behavior(
        user_id=current_user.id,
        behavior_type="unban_user",
        target_type="user",
        target_id=user_id
    )

    return ResponseModel.success(data={"user_id": user_id, "is_active": True, "status": "正常"}, message="用户已解封")


@router.get(
    "/users/{user_id}",
    response_model=ResponseModel[UserResponse],
    summary="查看用户详情（管理员）"
)
async def get_user_detail(
    user_id: int,
    current_user: UserResponse = Depends(require_admin)
):
    """
    查看用户详情（管理员）

    **功能描述**：管理员可查看任意用户的详细信息。

    **路径参数**：
    - `user_id`: 用户ID

    **错误码**：
    - 403: 无管理员权限
    - 404: 用户不存在
    """
    user = await Users.get_or_none(id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return ResponseModel.success(data=UserResponse.model_validate(user), message="获取成功")


@router.get(
    "/users",
    response_model=ResponseModel[UserListResponse],
    summary="获取用户列表（管理员）"
)
async def get_user_list(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="账户状态筛选：true=正常，false=封禁"),
    current_user: UserResponse = Depends(require_admin)
):
    """
    获取用户列表（管理员）

    **功能描述**：管理员可分页查看平台用户列表，支持按账户状态筛选。

    **查询参数**：
    - `page`: 页码（默认1）
    - `limit`: 每页数量（默认20，最大100）
    - `is_active`: 账户状态筛选（true=正常，false=封禁）

    **返回内容**：
    - total: 用户总数
    - users: 用户列表

    **错误码**：
    - 403: 无管理员权限
    """
    query = Users.all()

    if is_active is not None:
        query = query.filter(is_active=is_active)

    total = await query.count()
    offset = (page - 1) * limit
    users = await query.offset(offset).limit(limit).order_by("-created_at").all()

    user_list = [UserResponse.model_validate(user) for user in users]

    return ResponseModel.success(
        data=UserListResponse(total=total, users=user_list),
        message="获取成功"
    )


# ==================== FD06-06 发布系统公告 ====================

@router.post(
    "/announcements",
    response_model=ResponseModel[dict],
    summary="发布系统公告（管理员）"
)
async def create_announcement(
    title: str = Query(..., min_length=1, max_length=100, description="公告标题"),
    content: str = Query(..., min_length=1, description="公告内容"),
    current_user: UserResponse = Depends(require_admin)
):
    """
    发布系统公告（管理员）

    **功能描述**：管理员编辑公告标题与正文内容并推送。

    **查询参数**：
    - `title`: 公告标题（最多100字符）
    - `content`: 公告内容

    **业务规则**：
    - 公告发布后将在所有用户首页顶部以横幅形式展示
    - 已登录用户的消息中心同步收到该公告通知
    - 系统公告从 messages 表发送，type='announcement'
    - recipient_id 为空表示系统消息

    **错误码**：
    - 403: 无管理员权限
    """
    await MessageDAO.send_announcement(
        title=title,
        content=content,
        sender_id=current_user.id
    )

    await UserService.log_user_behavior(
        user_id=current_user.id,
        behavior_type="publish_announcement",
        target_type="announcement",
        target_id=0
    )

    return ResponseModel.success(data={"title": title}, message="公告发布成功")


# ==================== FD06-07 查看平台数据概览 ====================

@router.get(
    "/stats/overview",
    response_model=ResponseModel[PlatformStatsResponse],
    summary="获取平台数据概览（管理员）"
)
async def get_platform_stats(
    days: int = Query(7, ge=1, le=30, description="统计天数范围"),
    current_user: UserResponse = Depends(require_admin)
):
    """
    获取平台数据概览（管理员）

    **功能描述**：管理员在后台仪表盘查看平台核心运营指标。

    **查询参数**：
    - `days`: 统计天数范围（默认7天，最大30天）

    **返回内容**：
    - 店铺总数、用户总数、评论总数
    - 近7日新增趋势（店铺、用户、评论）
    - 每日新增数据列表

    **数据来源**：
    - 店铺总数：COUNT(*) FROM shops WHERE is_active=True
    - 用户总数：COUNT(*) FROM users WHERE is_active=True
    - 评论总数：COUNT(*) FROM comments WHERE is_active=True
    - 近7日新增：按 created_at 分组统计

    **错误码**：
    - 403: 无管理员权限
    """
    total_shops = await Shops.filter(is_active=True).count()
    total_users = await Users.filter(is_active=True).count()
    total_comments = await Comments.filter(is_active=True).count()

    date_from = datetime.now() - timedelta(days=days)

    active_shops_7d = await Shops.filter(is_active=True, created_at__gte=date_from).count()
    active_users_7d = await Users.filter(is_active=True, created_at__gte=date_from).count()
    active_comments_7d = await Comments.filter(is_active=True, created_at__gte=date_from).count()

    daily_stats = []
    for i in range(days):
        day_date = datetime.now() - timedelta(days=i)
        day_start = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        new_shops = await Shops.filter(is_active=True, created_at__gte=day_start, created_at__lte=day_end).count()
        new_users = await Users.filter(is_active=True, created_at__gte=day_start, created_at__lte=day_end).count()
        new_comments = await Comments.filter(is_active=True, created_at__gte=day_start, created_at__lte=day_end).count()

        daily_stats.append(DailyStatsItem(
            date=day_start.strftime("%Y-%m-%d"),
            new_shops=new_shops,
            new_users=new_users,
            new_comments=new_comments
        ))

    daily_stats.reverse()

    stats = PlatformStatsResponse(
        total_shops=total_shops,
        total_users=total_users,
        total_comments=total_comments,
        active_shops_7d=active_shops_7d,
        active_users_7d=active_users_7d,
        active_comments_7d=active_comments_7d,
        daily_stats=[d.model_dump() for d in daily_stats]
    )

    return ResponseModel.success(data=stats, message="获取成功")
