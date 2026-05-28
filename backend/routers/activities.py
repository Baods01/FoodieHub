from fastapi import APIRouter, Depends, Query

from schemas.common import ResponseModel
from schemas.users import UserResponse
from dao.activity_dao import ActivityDAO
from utils.auth import get_current_user

router = APIRouter(tags=["动态模块"])


@router.get("/users/me/activities", response_model=ResponseModel, summary="我的动态")
async def get_my_activities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
):
    """当前用户的动态时间线（评论、评分、收藏等）。"""
    data = await ActivityDAO.list_by_user(current_user.id, page=page, page_size=page_size)
    return ResponseModel.success(data=data)


@router.get("/users/{user_id}/activities", response_model=ResponseModel, summary="用户动态")
async def get_user_activities(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
):
    """指定用户的公开动态时间线（个人主页用）。"""
    data = await ActivityDAO.list_by_user(user_id, page=page, page_size=page_size)
    return ResponseModel.success(data=data)
