from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from dependencies.auth import oauth2_scheme, get_current_user
from schemas.favorites import (
    FavoriteCreate,
    FavoriteResponse,
    FavoriteActionResponse
)
from schemas.users import UserResponse
from services.favorite_service import FavoriteService

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post("/toggle", response_model=FavoriteActionResponse)
async def toggle_favorite(
    favorite_data: FavoriteCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    收藏/取消收藏店铺（切换状态）
    - 采用乐观更新策略，前端先更新UI，后端异步持久化
    - 如果已收藏，则取消收藏
    - 如果未收藏，则添加收藏
    """
    if current_user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        result = await FavoriteService.toggle_favorite(current_user.id, favorite_data.shop_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.post("/favorite", response_model=FavoriteActionResponse)
async def favorite_shop(
    favorite_data: FavoriteCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    收藏店铺
    """
    if current_user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        result = await FavoriteService.favorite_shop(current_user.id, favorite_data.shop_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"收藏失败: {str(e)}")


@router.post("/unfavorite", response_model=FavoriteActionResponse)
async def unfavorite_shop(
    favorite_data: FavoriteCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    取消收藏
    """
    if current_user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        result = await FavoriteService.unfavorite_shop(current_user.id, favorite_data.shop_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消收藏失败: {str(e)}")


@router.get("/user")
async def get_user_favorites(
    current_user: UserResponse = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """
    获取用户收藏列表
    """
    if current_user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        favorites = await FavoriteService.get_user_favorites(current_user.id, limit, offset)
        return {"total": len(favorites), "favorites": jsonable_encoder(favorites)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收藏列表失败: {str(e)}")


@router.get("/shop/{shop_id}/count")
async def get_shop_favorite_count(shop_id: int):
    """
    获取店铺收藏数
    """
    try:
        count = await FavoriteService.get_shop_favorite_count(shop_id)
        return {"shop_id": shop_id, "favorite_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收藏数失败: {str(e)}")