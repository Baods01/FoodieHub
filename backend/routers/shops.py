from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from schemas.shops import ShopCreate, ShopUpdate, ShopResponse, MenuItemResponse, RatingCreate, RatingResponse, MenuItemCreateRequest
from schemas.common import ResponseModel
from schemas.users import UserResponse
from services import ShopService, FavoriteService, LogService
from utils.auth import get_current_user, require_login, require_admin

router = APIRouter(tags=["店铺模块"])


# ==================== Shops ====================

@router.post("/shops", response_model=ResponseModel[ShopResponse], summary="创建店铺")
async def create_shop(
    data: ShopCreate,
    current_user: UserResponse = Depends(require_login),
):
    """
    创建店铺接口
    
    请求参数 (ShopCreate):
    - name (string, 必填): 店铺名称，长度1-100字符
    - dict_data_ids (array[int], 必填): 字典数据ID列表，至少包含一个品类ID和一个区域ID
    - menu_items (array[MenuItemCreateRequest], 可选): 初始菜单项列表
    
    响应:
    - 成功返回创建的店铺信息
    - 失败返回错误信息
    """
    try:
        shop = await ShopService.create(
            name=data.name,
            dict_data_ids=data.dict_data_ids,
            menu_items=[m.model_dump() for m in data.menu_items] if data.menu_items else None,
        )
        await LogService.log(action="create_shop", operator=current_user, target_type="shop", target_id=shop.id)
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
    """
    搜索店铺接口
    
    查询参数:
    - keyword (string, 可选): 搜索关键词
    - category_ids (array[int], 可选): 品类ID列表
    - district_ids (array[int], 可选): 区域ID列表
    - min_rating (float, 可选): 最低评分，范围0-5
    - sort_by (string, 可选): 排序字段，可选值为 "created_at"、"average_rating"、"view_count"、"favorite_count"，默认值为 "favorite_count"
    - sort_order (string, 可选): 排序方式，可选值为 "asc"、"desc"，默认值为 "desc"
    - page (integer, 可选): 页码，默认值为 1
    - page_size (integer, 可选): 每页大小，默认值为 20，最大值为 100
    
    响应:
    - 成功返回店铺搜索结果
    - 失败返回错误信息
    """
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
    if shop.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该店铺已被封禁",
        )
    if user_id:
        await LogService.log(action="view_shop", operator=None, operator_name=current_user.username if current_user else None, target_type="shop", target_id=shop_id)
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
        await LogService.log(action="update_shop", operator=current_user, target_type="shop", target_id=shop_id)
        return ResponseModel.success(data=shop, message="更新成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/shops/{shop_id}", response_model=ResponseModel, summary="删除店铺（管理员）")
async def delete_shop(shop_id: int, current_user: UserResponse = Depends(require_admin)):
    ok = await ShopService.delete(shop_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="店铺不存在")
    await LogService.log(action="delete_shop", operator=current_user, target_type="shop", target_id=shop_id)
    return ResponseModel.success(data={}, message="删除成功")


# ==================== Ratings ====================

@router.post("/shops/{shop_id}/rating", response_model=ResponseModel, summary="评分")
async def rate_shop(
    shop_id: int,
    data: RatingCreate,
    current_user: UserResponse = Depends(require_login),
):
    """
    评分店铺接口
    
    请求参数 (RatingCreate):
    - score (integer, 必填): 评分值，范围1-5
    
    响应:
    - 成功返回评分结果
    - 失败返回错误信息
    """
    result = await ShopService.rate(shop_id, current_user.id, data.score)
    await LogService.log(action="rate_shop", operator=current_user, target_type="shop", target_id=shop_id, detail={"score": data.score})
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
    """
    添加菜品接口
    
    查询参数:
    - name (string, 必填): 菜品名称，长度1-100字符
    - price (float, 可选): 价格，必须大于0
    - description (string, 可选): 菜品描述，最大500字符
    
    响应:
    - 成功返回添加的菜品信息
    - 失败返回错误信息
    """
    item = await ShopService.add_menu_item(shop_id, name, price=price, description=description)
    return ResponseModel.success(data=item, message="添加成功")


@router.post("/shops/{shop_id}/menu/batch", response_model=ResponseModel, summary="批量添加菜品")
async def add_menu_items_batch(
    shop_id: int,
    items: List[MenuItemCreateRequest],
    current_user: UserResponse = Depends(require_login),
):
    """
    批量添加菜品接口
    
    请求体参数:
    - items (array[MenuItemCreateRequest], 必填): 菜品列表
    
    响应:
    - 成功返回添加的菜品列表
    - 失败返回错误信息
    """
    items_data = []
    for item in items:
        added_item = await ShopService.add_menu_item(
            shop_id, 
            item.name, 
            price=item.price, 
            description=item.description
        )
        items_data.append(added_item)
    
    return ResponseModel.success(data=items_data, message=f"成功添加 {len(items_data)} 个菜品")


# ==================== Favorites ====================

@router.post("/favorites/toggle", response_model=ResponseModel, summary="切换收藏")
async def toggle_favorite(
    shop_id: int = Query(...),
    current_user: UserResponse = Depends(require_login),
):
    """
    切换收藏接口
    
    查询参数:
    - shop_id (integer, 必填): 店铺ID
    
    响应:
    - 成功返回收藏状态
    - 失败返回错误信息
    """
    result = await FavoriteService.toggle(current_user.id, shop_id)
    await LogService.log(action="toggle_favorite", operator=current_user, target_type="shop", target_id=shop_id)
    return ResponseModel.success(data=result, message="操作成功")


@router.get("/favorites/user", response_model=ResponseModel, summary="收藏列表")
async def list_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_login),
):
    """
    收藏列表接口
    
    查询参数:
    - page (integer, 可选): 页码，默认值为 1
    - page_size (integer, 可选): 每页大小，默认值为 20，最大值为 100
    
    响应:
    - 成功返回收藏列表
    - 失败返回错误信息
    """
    result = await FavoriteService.list(current_user.id, page=page, page_size=page_size)
    return ResponseModel.success(data=result, message="获取成功")
