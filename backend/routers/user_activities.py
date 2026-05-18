from fastapi import APIRouter, Depends, HTTPException

from dependencies.auth import oauth2_scheme, get_current_user
from schemas.users import UserResponse
from services.user_activities_service import UserActivitiesService

router = APIRouter()


@router.get("/users/me/activities", summary="获取我的动态列表")
async def get_my_activities(
    type: str = None,
    limit: int = 20,
    offset: int = 0,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    获取当前用户的动态列表（按时间倒序）
    
    - **type**: 活动类型（可选）：rating=评分, comment=评论, like=点赞, favorite=收藏
    - **limit**: 每页数量
    - **offset**: 偏移量
    """
    if current_user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        user_id = current_user.id
        
        activities = await UserActivitiesService.get_user_activities(
            user_id=user_id,
            type=type,
            limit=limit,
            offset=offset
        )
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "items": activities["items"],
                "total": activities["total"],
                "has_more": activities["has_more"]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/users/{user_id}/activities", summary="获取用户动态列表")
async def get_user_activities(
    user_id: int,
    type: str = None,
    limit: int = 20,
    offset: int = 0,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    获取指定用户的动态列表（按时间倒序）
    
    - **user_id**: 用户ID
    - **type**: 活动类型（可选）：rating=评分, comment=评论, like=点赞, favorite=收藏
    - **limit**: 每页数量
    - **offset**: 偏移量
    """
    try:
        activities = await UserActivitiesService.get_user_activities(
            user_id=user_id,
            type=type,
            limit=limit,
            offset=offset
        )
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "items": activities["items"],
                "total": activities["total"],
                "has_more": activities["has_more"]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")
