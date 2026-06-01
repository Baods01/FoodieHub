from fastapi import APIRouter, Depends, Query

from schemas.common import ResponseModel
from schemas.users import UserResponse
from services.activity_service import ActivityService
from utils.auth import get_current_user

router = APIRouter(tags=["动态模块"])


@router.get("/users/me/activities", response_model=ResponseModel, summary="我的动态")
async def get_my_activities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    我的动态接口
    
    查询参数:
    - page (integer, 可选): 页码，默认值为 1
    - page_size (integer, 可选): 每页大小，默认值为 20，最大值为 100
    
    响应:
    - 成功返回动态列表
    - 失败返回错误信息
    """
    data = await ActivityService.list_by_user(current_user.id, page=page, page_size=page_size)
    return ResponseModel.success(data=data)


@router.get("/users/{user_id}/activities", response_model=ResponseModel, summary="用户动态")
async def get_user_activities(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    用户动态接口
    
    查询参数:
    - page (integer, 可选): 页码，默认值为 1
    - page_size (integer, 可选): 每页大小，默认值为 20，最大值为 100
    
    响应:
    - 成功返回动态列表
    - 失败返回错误信息
    """
    data = await ActivityService.list_by_user(user_id, page=page, page_size=page_size)
    return ResponseModel.success(data=data)
