from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from schemas.shops import ShopCreate, ShopUpdate, ShopResponse, ShopListItem, MenuItemResponse
from schemas.common import ResponseModel
from schemas.users import UserResponse
from services import ShopService, FavoriteService
from utils.auth import get_current_user, require_login, require_admin

router = APIRouter(tags=["店铺模块"])


# ==================== Shops ====================

@router.post("/shops", response_model=ResponseModel[ShopResponse], summary="创建店铺")
async def create_shop(
    data: ShopCreate,
    current_user: UserResponse = Depends(require_login),
):
    try:
        shop = await ShopService.create(
            name=data.name,
            dict_data_ids=data.dict_data_ids,
            menu_items=[m.model_dump() for m in data.menu_items] if data.menu_items else None,
        )
        return ResponseModel.success(data=shop, message="店铺创建成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/shops", response_model=ResponseModel, summary="搜索店铺")
async def search_shops(
    keyword: Optional[str] = Query(None),
    category_ids: Optional[List[int]] = Query(None),
    district_ids: Optional[List[int]] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    sort_by: str = Query("favorite_count", pattern="^(created_at|average_rating|view_count|favorite_count)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
):
    user_id = current_user.id if current_user else None
    result = await ShopService.search(
        keyword=keyword, category_ids=category_ids, district_ids=district_ids,
        min_rating=min_rating, sort_by=sort_by, sort_order=sort_order,
        page=page, page_size=page_size, user_id=user_id,
    )
    return ResponseModel.success(data=result, message="获取成功")


@router.get("/shops/{shop_id}", response_model=ResponseModel[ShopResponse], summary="店铺详情")
async def get_shop_detail(
    shop_id: int,
    current_user: UserResponse = Depends(get_current_user),
):
    user_id = current_user.id if current_user else None
    shop = await ShopService.get_by_id(shop_id, user_id=user_id)
    if not shop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="店铺不存在")
    return ResponseModel.success(data=shop, message="获取成功")


@router.put("/shops/{shop_id}", response_model=ResponseModel[ShopResponse], summary="更新店铺（管理员）")
async def update_shop(
    shop_id: int,
    data: ShopUpdate,
    current_user: UserResponse = Depends(require_admin),
):
    try:
        shop = await ShopService.update(
            shop_id=shop_id, name=data.name,
            dict_data_ids=data.dict_data_ids,
            is_active=data.is_active,
        )
        if not shop:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="店铺不存在")
        return ResponseModel.success(data=shop, message="更新成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/shops/{shop_id}", response_model=ResponseModel, summary="删除店铺（管理员）")
async def delete_shop(shop_id: int, current_user: UserResponse = Depends(require_admin)):
    ok = await ShopService.delete(shop_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="店铺不存在")
    return ResponseModel.success(data={}, message="删除成功")


# ==================== Ratings ====================

@router.post("/shops/{shop_id}/rating", response_model=ResponseModel, summary="评分")
async def rate_shop(
    shop_id: int,
    score: int = Query(..., ge=1, le=5),
    current_user: UserResponse = Depends(require_login),
):
    result = await ShopService.rate(shop_id, current_user.id, score)
    return ResponseModel.success(data=result, message="评分成功")


# ==================== Menu ====================

@router.get("/shops/{shop_id}/menu", response_model=ResponseModel, summary="菜单列表")
async def get_menu(shop_id: int, current_user: UserResponse = Depends(get_current_user)):
    items = await ShopService.get_menu(shop_id)
    return ResponseModel.success(data=items, message="获取成功")


@router.post("/shops/{shop_id}/menu", response_model=ResponseModel, summary="添加菜品")
async def add_menu_item(
    shop_id: int,
    name: str = Query(..., min_length=1),
    price: Optional[float] = Query(None, gt=0),
    description: Optional[str] = Query(None),
    current_user: UserResponse = Depends(require_login),
):
    item = await ShopService.add_menu_item(shop_id, name, price=price, description=description)
    return ResponseModel.success(data=item, message="添加成功")


# ==================== Favorites ====================

@router.post("/favorites/toggle", response_model=ResponseModel, summary="切换收藏")
async def toggle_favorite(
    shop_id: int = Query(...),
    current_user: UserResponse = Depends(require_login),
):
    result = await FavoriteService.toggle(current_user.id, shop_id)
    return ResponseModel.success(data=result, message="操作成功")


@router.get("/favorites/user", response_model=ResponseModel, summary="收藏列表")
async def list_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_login),
):
    result = await FavoriteService.list(current_user.id, page=page, page_size=page_size)
    return ResponseModel.success(data=result, message="获取成功")
