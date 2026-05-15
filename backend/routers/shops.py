from fastapi import APIRouter, HTTPException, status, Depends, Request, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, RedirectResponse
from typing import Optional, List
import traceback
import os
from pathlib import Path
from datetime import datetime

from schemas.shops import (
    ShopCreate, ShopResponse, ShopUpdate,
    RatingCreate, ShopSearchRequest,
    ShopListItem, ShopMergeResult, MenuItemResponse, MenuItemAddRequest
)
from schemas.comments import CommentCreateRequest, CommentResponse
from schemas.images import ImageUploadRequest, MenuItemWithImageRequest
from schemas.reviews import (
    ShopEditRequestCreate, ShopDuplicateRequestCreate,
    ShopEditRequestApprove, ShopEditRequestReject,
    ShopEditRequestListRequest, ShopEditRequestResponse
)
from schemas.common import ResponseModel
from schemas.users import UserResponse
from services.shop_service import ShopService
from dependencies.auth import get_current_user, require_login

# 调试日志开关
DEBUG_LOG = True

router = APIRouter(prefix="/shops", tags=["店铺模块"])


# ============ 店铺基本操作 ============

@router.post("/", response_model=ResponseModel[ShopResponse], summary="创建店铺")
async def create_shop(
    request: Request,
    shop_data: ShopCreate,
    current_user: UserResponse = Depends(require_login)
):
    """
    创建新店铺（无需审核，创建即上线）

    **必填字段：**
    - `name`: 店铺名称
    - `dict_data_codes`: 字典数据编码列表（至少选择一个区域和一个品类）

    **可选字段（新增）：**
    - `description`: 店铺描述、可将人均消费以及更详细的地址写入其中（最多2000字符）
    - `price_range`: 人均消费价格段，如 `'30-50'` 或 `'50-100'`
    - `business_hours`: 营业时间，如 `'08:00-22:00'`
    - `dining_methods`: 就餐方式数组，如 `['dine_in', 'pickup', 'delivery']`
      - `dine_in`: 堂食
      - `pickup`: 自取
      - `delivery`: 外卖
    - `address_detail`: 详细地址（最多200字符）
    - `tags`: 店铺标签数组，如 `['环境好', '速度快', '性价比高']`
    - `menu_items`: 菜单项列表（可选，创建时可提交初始菜单）

    **菜单项格式：**
    ```json
    "menu_items": [
        {
            "name": "菜品名称",
            "price": 25.5,
            "description": "菜品描述"
        }
    ]
    ```

    **预设字典数据编码：**

    **品类编码（8个）：**
    - `local_cuisine`: 地方菜
    - `hotpot`: 火锅
    - `barbecue`: 烧烤/烤肉
    - `western_food`: 异域料理
    - `snacks`: 小吃快餐
    - `specialty`: 特色菜
    - `drinks`: 饮品
    - `desserts`: 甜点/面包

    **区域编码（5个）：**
    - `nei_taisan`: 泰山区
    - `nei_huashan`: 华山区
    - `nei_qilin`: 启林区
    - `nei_liuyi`: 六一区
    - `wai_outside`: 校外

    **后端自动生成：**
    - `id`: 店铺ID（自增主键）
    - `view_count`, `favorite_count`, `comment_count`: 初始值为 0
    - `average_rating`: 初始值为 0.0

    **前置条件：**
    - 用户已登录
    - 店铺名称未被占用
    - 所有字典数据编码必须存在于数据库中

    **后置条件：**
    - 店铺数据写入数据库
    - 店铺关联的字典数据建立关联关系
    - 返回完整的店铺信息（包含字典数据、菜单项等）
    """
    # 调试：打印请求头
    print(f"DEBUG create_shop: Headers: {dict(request.headers)}")
    print(f"DEBUG create_shop: Authorization header: {request.headers.get('authorization', 'Not found')}")
    try:
        shop = await ShopService.create_shop(current_user.id, shop_data)
        return ResponseModel.success(data=shop, message="店铺创建成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        # 打印详细错误信息到终端
        print(f"Error creating shop: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"店铺创建失败: {str(e)}"
        )


@router.get("/", response_model=ResponseModel[dict], summary="浏览/搜索店铺列表")
async def search_shops(
    keyword: Optional[str] = Query(None, max_length=100, description="搜索关键词（店铺名称、描述）"),
    category_codes: Optional[List[str]] = Query(None, description="品类筛选（编码列表）"),
    district_codes: Optional[List[str]] = Query(None, description="区域筛选（编码列表）"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="最低评分筛选"),
    sort_by: str = Query("favorite_count", pattern="^(created_at|average_rating|view_count|favorite_count)$", description="排序字段"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="排序方向"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    浏览或搜索店铺列表（支持游客访问）

    **功能描述：**
    - 用户进入平台首页或发现页后，系统展示店铺卡片列表
    - 默认按收藏数降序排列，优先展示社区成员广泛标记的店铺
    - 支持关键词搜索、分类筛选、区域筛选
    - 支持多种排序方式

    **支持的筛选条件：**
    - `keyword`: 关键词搜索（店铺名称、描述）
    - `category_codes`: 品类筛选（编码列表，如 ['hotpot', 'snacks']）
    - `district_codes`: 区域筛选（编码列表，如 ['nei_taisan', 'nei_huashan']）
    - `min_rating`: 最低评分筛选（0-5）

    **排序参数：**
    - `sort_by`: 排序字段（created_at、average_rating、view_count、favorite_count）
    - `sort_order`: 排序方向（asc、desc）

    **分页参数：**
    - `page`: 页码（从 1 开始）
    - `page_size`: 每页数量（默认 20，最大 100）

    **预设字典数据编码：**

    **品类编码（8个）：**
    - `local_cuisine`: 地方菜
    - `hotpot`: 火锅
    - `barbecue`: 烧烤/烤肉
    - `western_food`: 异域料理
    - `snacks`: 小吃快餐
    - `specialty`: 特色菜
    - `drinks`: 饮品
    - `desserts`: 甜点/面包

    **区域编码（5个）：**
    - `nei_taisan`: 泰山区
    - `nei_huashan`: 华山区
    - `nei_qilin`: 启林区
    - `nei_liuyi`: 六一区
    - `wai_outside`: 校外
    """
    try:
        result = await ShopService.search_shops(
            keyword=keyword,
            category_codes=category_codes,
            district_codes=district_codes,
            min_rating=min_rating,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        return ResponseModel.success(data=result, message="获取成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取店铺列表失败"
        )


@router.get("/{shop_id}", response_model=ResponseModel[ShopResponse], summary="查看店铺详情")
async def get_shop_detail(
    shop_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    查看店铺详情（支持游客访问）

    **功能：**
    - 增加店铺浏览量
    - 返回完整的店铺信息（包括字典数据、菜单项、图片等）
    - 返回评分分布统计
    - 返回当前用户的收藏状态和评分（已登录用户）
    - 游客可查看店铺信息，但互动功能需登录

    **详情页信息区域：**
    1. 店铺封面图与基本信息区（名称、区域、品类、收藏数、浏览量）
    2. 菜单图片展示区（若有）
    3. 环境图片展示区（若有）
    4. 详细评分分布区（显示1-5星各档评分人数）
    5. 用户图文评论列表区
    6. 问答讨论区

    **注意：**
    - 若店铺因违规被管理员封禁，页面显示"该店铺已被封禁"提示
    """
    try:
        user_id = current_user.id if current_user else None
        redirect_target = await ShopService.get_shop_redirect_target(shop_id)
        if redirect_target:
            return RedirectResponse(url=f"/shops/{redirect_target}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

        shop = await ShopService.get_shop_detail(shop_id, user_id)
        return ResponseModel.success(data=shop, message="获取成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取店铺详情失败"
        )


# ============ 管理员操作 ============

@router.put("/{shop_id}", response_model=ResponseModel[ShopResponse], summary="更新店铺信息")
async def update_shop(
    shop_id: int,
    update_data: ShopUpdate,
    current_user: UserResponse = Depends(require_login)
):
    """
    更新店铺信息（仅管理员）
    
    支持部分字段更新，未传入的字段将保持不变。

    **可更新字段：**
    - `name`: 店铺名称
    - `description`: 店铺描述
    - `is_active`: 是否启用（软删除）
    - `location_codes`: 区域编码列表（如：['nei_taisan', 'nei_huashan']）
    - `category_codes`: 品类编码列表（如：['local_cuisine', 'hotpot']）

    **管理员权限：**
    - 修改店铺基本信息
    - 软删除店铺
    """
    try:
        # 检查是否为管理员
        if current_user.role != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限执行此操作"
            )
        shop = await ShopService.update_shop(shop_id, update_data)
        return ResponseModel.success(data=shop, message="更新成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新店铺信息失败"
        )


@router.delete("/{shop_id}", response_model=ResponseModel[dict], summary="删除店铺")
async def delete_shop(
    shop_id: int,
    current_user: UserResponse = Depends(require_login)
):
    """
    删除店铺（仅管理员）

    **管理员权限：**
    - 软删除店铺
    """
    try:
        # 检查是否为管理员
        if current_user.role != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限执行此操作"
            )
        success = await ShopService.delete_shop(shop_id)
        if success:
            return ResponseModel.success(data={}, message="删除成功")
        raise ValueError("店铺不存在")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除店铺失败"
        )


@router.post("/edit-request", response_model=ResponseModel[dict], summary="提交店铺信息勘误反馈")
async def submit_shop_edit_request(
    edit_request: ShopEditRequestCreate,
    current_user: UserResponse = Depends(require_login)
):
    """
    提交店铺信息勘误反馈，只有管理员审核后才会生效

    **请求体字段：**
    - `shop_id`: 店铺ID（必填）
    - `name`: 新的店铺名称（可选）
    - `area_dict_data_id`: 新的区域字典数据ID（可选）
    - `category_dict_data_id`: 新的品类字典数据ID（可选）
    - `reason`: 修改原因说明（可选）

    **字典数据ID说明：**

    **区域字典数据ID：**
    - 9: 泰山区 (nei_taisan)
    - 10: 华山区 (nei_huashan)
    - 11: 启林区 (nei_qilin)
    - 12: 六一区 (nei_liuyi)
    - 13: 校外 (wai_outside)
    - 14: 主校区 (zhuxiaoqu)

    **品类字典数据ID：**
    - 1: 地方菜 (local_cuisine)
    - 2: 火锅 (hotpot)
    - 3: 烧烤/烤肉 (barbecue)
    - 4: 异域料理 (western_food)
    - 5: 小吃快餐 (snacks)
    - 6: 特色菜 (specialty)
    - 7: 饮品 (drinks)
    - 8: 甜点/面包 (desserts)

    **注意事项：**
    - 至少提供一个修改项（name、area_dict_data_id 或 category_dict_data_id）
    - 如果只修改部分字段，其他字段将保持不变
    - 同一用户对同一字段7天内只能提交一次反馈
    - 同一店铺当天反馈数量上限为500条
    - 所有字典数据ID必须存在于系统中
    """
    from utils.logger import debug_logger

    debug_logger.info(f"[API] 收到勘误反馈请求 - user_id: {current_user.id}, request_data: {edit_request.dict()}")
    try:
        request_obj = await ShopService.submit_shop_correction_request(
            current_user.id,
            edit_request.shop_id,
            edit_request.name,
            edit_request.area_dict_data_id,
            edit_request.category_dict_data_id,
            edit_request.reason
        )
        debug_logger.info(f"[API] 勘误反馈提交成功 - request_id: {request_obj.id}")
        return ResponseModel.success(data={"request_id": request_obj.id}, message="反馈提交成功，等待管理员审核")
    except ValueError as e:
        debug_logger.warning(f"[API] 勘误反馈业务错误 - user_id: {current_user.id}, error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        debug_logger.error(f"[API] 勘误反馈未知错误 - user_id: {current_user.id}, error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="提交反馈失败"
        )


@router.post("/duplicate-request", response_model=ResponseModel[dict], summary="提交重复店铺反馈")
async def submit_shop_duplicate_request(
    duplicate_request: ShopDuplicateRequestCreate,
    current_user: UserResponse = Depends(require_login)
):
    """提交疑似重复店铺反馈，只有管理员审核后才会生效"""
    try:
        request_obj = await ShopService.submit_duplicate_shop_request(
            current_user.id,
            duplicate_request.candidate_shop_ids,
            duplicate_request.reason
        )
        return ResponseModel.success(data={"request_id": request_obj.id}, message="重复反馈提交成功，等待管理员审核")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="提交重复反馈失败"
        )


@router.get("/edit-requests", response_model=ResponseModel[dict], summary="查询店铺编辑/重复反馈列表")
async def list_shop_edit_requests(
    status: Optional[str] = Query(None, pattern="^(pending|approved|rejected)$", description="状态筛选"),
    shop_id: Optional[int] = Query(None, description="店铺ID筛选"),
    user_id: Optional[int] = Query(None, description="提交用户ID筛选"),
    current_user: UserResponse = Depends(require_login)
):
    """管理员获取店铺编辑与重复反馈列表"""
    try:
        if current_user.role != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限执行此操作"
            )
        result = await ShopService.list_shop_edit_requests(status=status, shop_id=shop_id, user_id=user_id)
        return ResponseModel.success(data=result, message="获取成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取反馈列表失败"
        )


@router.post("/edit-requests/{request_id}/approve", response_model=ResponseModel[dict], summary="审核通过店铺编辑请求")
async def approve_shop_edit_request(
    request_id: int,
    approve_data: ShopEditRequestApprove,
    current_user: UserResponse = Depends(require_login)
):
    """管理员审核通过某条店铺编辑/重复反馈请求"""
    try:
        if current_user.role != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限执行此操作"
            )
        await ShopService.approve_shop_edit_request(request_id, current_user.id, approve_data.main_shop_id)
        return ResponseModel.success(data={}, message="审核通过")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="审核通过失败"
        )


@router.post("/edit-requests/{request_id}/reject", response_model=ResponseModel[dict], summary="拒绝店铺编辑请求")
async def reject_shop_edit_request(
    request_id: int,
    reject_data: ShopEditRequestReject,
    current_user: UserResponse = Depends(require_login)
):
    """管理员拒绝某条店铺编辑/重复反馈请求"""
    try:
        if current_user.role != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限执行此操作"
            )
        await ShopService.reject_shop_edit_request(request_id, current_user.id, reject_data.reason)
        return ResponseModel.success(data={}, message="已拒绝")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="拒绝失败"
        )


# ============ 店铺扩展操作 ============

@router.post("/{shop_id}/rating", response_model=ResponseModel[dict], summary="对店铺评分")
async def rate_shop(
    shop_id: int,
    rating_data: RatingCreate,
    current_user: UserResponse = Depends(require_login)
):
    """
    用户对店铺评分（1-5）

    **规则：**
    - 每个用户对同一店铺只能评一次
    - 可以修改已有的评分
    - 修改后会重新计算店铺的平均评分
    """
    try:
        rating = await ShopService.rate_shop(current_user.id, shop_id, rating_data)
        return ResponseModel.success(data={"message": "评分成功"}, message="评分成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="评分失败"
        )


@router.post("/{shop_id}/comments", response_model=ResponseModel[dict], summary="创建评论/提问")
async def create_comment(
    shop_id: int,
    comment_data: CommentCreateRequest,
    current_user: UserResponse = Depends(require_login)
):
    """
    创建评论/提问（纯文字）

    **功能：**
    - 用户可在店铺详情页发表评论
    - 评论内容必填，1-500字符
    - 评论成功后，店铺评论数自动加1

    **前置条件：**
    - 用户已登录
    - 店铺状态正常
    - 用户账号状态正常

    **后置条件：**
    - 评论表中新增一条记录
    - 店铺评论数加1

    **参数解释**
    - **content**: 评论内容，必填，1-500字符
    - **type**: 评论类型，默认为 "comment"，可切换为question（提问）
    - **parent_id**: 父评论ID，回复评论时填写
    """
    try:
        if DEBUG_LOG:
            print(f"DEBUG create_comment route: user_id={current_user.id}, shop_id={shop_id}")
            print(f"DEBUG create_comment route: comment_data={comment_data.model_dump()}")
        comment = await ShopService.create_comment(current_user.id, shop_id, comment_data)
        return ResponseModel.success(data={"message": "评论创建成功"}, message="评论创建成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        if DEBUG_LOG:
            print(f"DEBUG create_comment route error: {str(e)}")
            print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评论创建失败: {str(e)}"
        )


@router.get("/{shop_id}/comments", response_model=ResponseModel[list], summary="获取评论列表")
async def get_shop_comments(
    shop_id: int,
    comment_type: Optional[str] = None,
    current_user: UserResponse = Depends(require_login)
):
    """
    获取店铺的评论/提问列表（一级评论）

    **支持的筛选：**
    - `comment_type`: 评论类型（comment=评论，question=提问）
    """
    try:
        if DEBUG_LOG:
            print(f"DEBUG get_shop_comments route: shop_id={shop_id}, comment_type={comment_type}, user_id={current_user.id}")
        
        comments = await ShopService.get_shop_comments(
            shop_id=shop_id,
            comment_type=comment_type,
            page=1,
            page_size=50,
            current_user_id=current_user.id
        )
        
        if DEBUG_LOG:
            print(f"DEBUG get_shop_comments route: Found {len(comments)} comments")
        
        return ResponseModel.success(data=comments, message="获取成功")
    except ValueError as e:
        if DEBUG_LOG:
            print(f"DEBUG get_shop_comments route ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        if DEBUG_LOG:
            import traceback
            print(f"DEBUG get_shop_comments route Error: {str(e)}")
            print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评论列表失败: {str(e)}"
        )


@router.get("/{shop_id}/comments/{comment_id}/replies", response_model=ResponseModel[list], summary="获取评论的子回复")
async def get_comment_replies(
    shop_id: int,
    comment_id: int,
    current_user: UserResponse = Depends(require_login)
):
    """
    获取某个评论的所有直接子回复/回答（二级评论）

    **功能：**
    - 返回指定评论的所有子回复
    - 子回复也包含用户信息和图片
    - 返回指定问题的所有回答（如果是提问）

    **参数解释**
    - **comment_id**: 评论/提问ID
    - **shop_id**: 店铺ID
    """
    try:
        if DEBUG_LOG:
            print(f"DEBUG get_comment_replies route: shop_id={shop_id}, comment_id={comment_id}, user_id={current_user.id}")
        
        replies = await ShopService.get_comment_replies(comment_id, current_user.id)
        
        if DEBUG_LOG:
            print(f"DEBUG get_comment_replies route: Found {len(replies)} replies")
        
        return ResponseModel.success(data=replies, message="获取成功")
    except Exception as e:
        if DEBUG_LOG:
            import traceback
            print(f"DEBUG get_comment_replies route Error: {str(e)}")
            print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取子回复失败: {str(e)}"
        )


@router.post("/{shop_id}/menu", response_model=ResponseModel[MenuItemResponse], summary="添加菜单项")
async def add_menu_item(
    shop_id: int,
    menu_item: MenuItemAddRequest,
    current_user: UserResponse = Depends(require_login)
):
    """
    为店铺添加菜单项（独立于创建店铺时的菜单）

    **必填字段：**
    - `name`: 菜品名称（必填，最多100字符）
    - `price`: 价格（必填，单位：元，必须大于0）

    **可选字段：**
    - `description`: 菜品描述（可选，最多500字符）

    **请求体格式：**
    ```json
    {
        "name": "菜品名称",
        "price": 25.5,
        "description": "菜品描述（可选）"
    }
    ```
    """
    try:
        result = await ShopService.add_menu_item(shop_id, menu_item)
        return ResponseModel.success(data=result, message="菜单项添加成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加菜单项失败"
        )


@router.get("/{shop_id}/menu", response_model=ResponseModel[list], summary="获取菜单列表")
async def get_menu_items(
    shop_id: int,
    current_user: UserResponse = Depends(require_login)
):
    """
    获取店铺的所有菜单项
    """
    try:
        menu_items = await ShopService.get_menu_items(shop_id)
        return ResponseModel.success(data=menu_items, message="获取成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取菜单列表失败"
        )


# ============ 图片上传接口 ============

# 图片上传配置
BASE_DIR = Path(__file__).resolve().parent  # FoodieHub/backend
UPLOAD_DIR = BASE_DIR / "static" / "images"
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB


async def save_uploaded_file(file: UploadFile) -> str:
    """
    保存上传的图片文件
    
    Returns:
        文件相对路径（如："static/images/2026/05/09/abc123.jpg"）
    """
    # 创建日期子目录
    now = datetime.now()
    date_dir = UPLOAD_DIR / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
    date_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成唯一文件名
    import uuid
    file_extension = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = date_dir / unique_filename
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 返回相对于 FoodieHub/backend 的路径
    return str(file_path.relative_to(BASE_DIR))


@router.post("/{shop_id}/images", response_model=ResponseModel[dict], summary="上传店铺环境图片")
async def upload_shop_image(
    shop_id: int,
    file: UploadFile = File(..., description="环境图片（支持jpg、png、gif、webp格式，最大2MB）"),
    current_user: UserResponse = Depends(require_login)
):
    """
    上传店铺环境图片
    
    **功能：**
    - 用户可为已上线的店铺上传环境图片
    - 图片格式校验：jpg、png、gif、webp
    - 图片大小限制：单张不超过 2MB
    
    **后置条件：**
    - 图片保存到服务器
    - 数据库记录图片信息
    - 其他用户可在店铺详情页查看图片
    """
    # 检查文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片格式。支持的格式：jpg、png、gif、webp"
        )
    
    # 检查文件大小
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片大小超过限制（最大 2MB）"
        )
    
    try:
        # 保存文件
        file_path = await save_uploaded_file(file)
        
        # 创建图片记录
        result = await ShopService.upload_shop_image(
            user_id=current_user.id,
            shop_id=shop_id,
            url=file_path,
            extra={
                "file_type": file.content_type,
                "file_size": len(content),
                "filename": file.filename
            }
        )
        
        return ResponseModel.success(
            data={"message": "图片上传成功", "image_id": result["image_id"], "url": file_path},
            message="图片上传成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片上传失败: {str(e)}"
        )


@router.post("/{shop_id}/menu-image", response_model=ResponseModel[dict], summary="上传菜单图片")
async def upload_menu_image(
    shop_id: int,
    file: UploadFile = File(..., description="菜单图片（支持jpg、png、gif、webp格式，最大2MB）"),
    current_user: UserResponse = Depends(require_login)
):
    """
    上传菜单图片（通用接口，可用于上传菜单封面或菜品图片）
    
    **功能：**
    - 上传菜单图片
    - 图片格式校验：jpg、png、gif、webp
    - 图片大小限制：单张不超过 2MB
    
    **后置条件：**
    - 图片保存到服务器
    - 数据库记录图片信息（entity_type='menu'）
    """
    # 检查文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片格式。支持的格式：jpg、png、gif、webp"
        )
    
    # 检查文件大小
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片大小超过限制（最大 2MB）"
        )
    
    try:
        # 保存文件
        file_path = await save_uploaded_file(file)
        
        # 创建图片记录（entity_type='menu' 表示菜单图片）
        result = await ShopService.upload_shop_image(
            user_id=current_user.id,
            shop_id=shop_id,
            url=file_path,
            extra={
                "file_type": file.content_type,
                "file_size": len(content),
                "filename": file.filename
            }
        )
        
        return ResponseModel.success(
            data={"message": "图片上传成功", "image_id": result["image_id"], "url": file_path},
            message="图片上传成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片上传失败: {str(e)}"
        )


@router.post("/{shop_id}/menu-items-image", response_model=ResponseModel[dict], summary="为菜单项上传图片")
async def upload_menu_item_image(
    shop_id: int,
    menu_id: int,
    file: UploadFile = File(..., description="菜品图片（支持jpg、png、gif、webp格式，最大2MB）"),
    current_user: UserResponse = Depends(require_login)
):
    """
    为菜单项上传图片（需提供 menu_id）
    
    **功能：**
    - 上传菜品图片
    - 图片格式校验：jpg、png、gif、webp
    - 图片大小限制：单张不超过 2MB
    
    **后置条件：**
    - 图片保存到服务器
    - 数据库记录图片信息（entity_type='menu_item'）
    - 图片URL存储在 menu_items 的 extra 字段中
    """
    # 检查文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片格式。支持的格式：jpg、png、gif、webp"
        )
    
    # 检查文件大小
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片大小超过限制（最大 2MB）"
        )
    
    try:
        # 保存文件
        file_path = await save_uploaded_file(file)
        
        # 创建图片记录并更新菜单项
        result = await ShopService.upload_menu_image(
            user_id=current_user.id,
            shop_id=shop_id,
            menu_id=menu_id,
            url=file_path,
            extra={
                "file_type": file.content_type,
                "file_size": len(content),
                "filename": file.filename
            }
        )
        
        return ResponseModel.success(
            data={"message": "菜单图片上传成功", "image_id": result["image_id"], "url": file_path},
            message="图片上传成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片上传失败: {str(e)}"
        )


@router.get("/{shop_id}/images", response_model=ResponseModel[List[dict]], summary="获取店铺图片列表")
async def get_shop_images(
    shop_id: int,
    current_user: UserResponse = Depends(require_login)
):
    """
    获取店铺的所有图片（环境图片）
    """
    try:
        images = await ShopService.get_shop_images(shop_id)
        return ResponseModel.success(data=images, message="获取成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取图片列表失败"
        )


@router.get("/{shop_id}/menu-images", response_model=ResponseModel[List[dict]], summary="获取菜单图片列表")
async def get_menu_item_images(
    shop_id: int,
    current_user: UserResponse = Depends(require_login)
):
    """
    获取菜单项的图片列表
    """
    try:
        menu_images = await ShopService.get_menu_item_images(shop_id)
        return ResponseModel.success(data=menu_images, message="获取成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取图片列表失败"
        )


# ============ 评论图片上传接口（FD02-03） ============

@router.post("/comments/{comment_id}/images", response_model=ResponseModel[dict], summary="为评论上传图片")
async def upload_comment_image(
    shop_id: int,
    comment_id: int,
    file: UploadFile = File(..., description="评论图片（支持jpg、png、gif、webp格式，最大2MB）"),
    current_user: UserResponse = Depends(require_login)
):
    """
    为评论上传图片（需提供 shop_id 和 comment_id 进行关联）
    
    **功能：**
    - 用户可在评论发表后上传图片
    - 图片格式校验：jpg、png、gif、webp
    - 图片大小限制：单张不超过 2MB
    
    **前置条件：**
    - 评论属于当前店铺
    - 用户是评论的作者
    
    **后置条件：**
    - 图片保存到服务器
    - 数据库记录图片信息（entity_type='comment'）
    """
    from schemas.comments import CommentResponse
    
    # 检查文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片格式。支持的格式：jpg、png、gif、webp"
        )
    
    # 检查文件大小
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片大小超过限制（最大 2MB）"
        )
    
    try:
        # 保存文件
        file_path = await save_uploaded_file(file)
        
        # 创建图片记录（entity_type='comment' 表示评论图片）
        result = await ShopService.upload_comment_image(
            user_id=current_user.id,
            shop_id=shop_id,
            comment_id=comment_id,
            url=file_path,
            extra={
                "file_type": file.content_type,
                "file_size": len(content),
                "filename": file.filename
            }
        )
        
        return ResponseModel.success(
            data={"message": "评论图片上传成功", "image_id": result["image_id"], "url": file_path},
            message="图片上传成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片上传失败: {str(e)}"
        )
