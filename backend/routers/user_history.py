from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from datetime import datetime

from schemas.user_history import (
    UserHistoryListRequest,
    UserHistoryListResponse,
    DeleteHistoryRequest,
    ClearHistoryResponse
)
from schemas.users import UserResponse
from services.shop_service import ShopService
from dependencies.auth import require_login

router = APIRouter(prefix="/user/history", tags=["用户浏览历史"])

@router.get("/", response_model=UserHistoryListResponse, summary="获取浏览历史记录")
async def get_user_history(
    request: UserHistoryListRequest = Depends(),
    current_user: UserResponse = Depends(require_login)
):
    """
    获取用户浏览历史记录
    
    **功能描述：**
    - 按浏览时间倒序分页展示
    - 支持时间范围筛选
    - 每条记录包含店铺封面图、名称、区域及最近浏览时间
    
    **参数说明：**
    - `page`: 页码，默认为1
    - `page_size`: 每页数量，默认为20，最大100
    - `start_time`: 开始时间筛选
    - `end_time`: 结束时间筛选
    - `shop_id`: 店铺ID筛选
    """
    try:
        result = await ShopService.get_user_view_history(
            user_id=current_user.id,
            page=request.page,
            page_size=request.page_size,
            start_time=request.start_time,
            end_time=request.end_time,
            shop_id=request.shop_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取浏览历史失败: {str(e)}"
        )


@router.delete("/{history_id}", response_model=dict, summary="删除单条浏览历史")
async def delete_history_item(
    history_id: int,
    current_user: UserResponse = Depends(require_login)
):
    """
    删除单条浏览历史记录
    
    **参数说明：**
    - `history_id`: 浏览历史记录ID
    """
    try:
        success = await ShopService.delete_user_view_history_item(
            user_id=current_user.id,
            history_id=history_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="浏览历史记录不存在或不属于当前用户"
            )
        return {"message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除浏览历史失败: {str(e)}"
        )


@router.delete("/", response_model=ClearHistoryResponse, summary="清空全部浏览历史")
async def clear_all_history(
    current_user: UserResponse = Depends(require_login)
):
    """
    清空用户全部浏览历史记录
    """
    try:
        deleted_count = await ShopService.clear_user_view_history(
            user_id=current_user.id
        )
        return {"deleted_count": deleted_count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清空浏览历史失败: {str(e)}"
        )