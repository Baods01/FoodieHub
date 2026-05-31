from fastapi import APIRouter, Depends, Query

from schemas.common import ResponseModel
from schemas.users import UserResponse
from services import LogService
from services.history_service import HistoryService
from utils.auth import require_login

router = APIRouter(tags=["浏览历史模块"])


@router.get("/users/me/history", response_model=ResponseModel, summary="浏览历史")
async def get_my_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_login),
):
    """当前用户的店铺浏览历史。"""
    data = await HistoryService.get_view_history(current_user.id, page=page, page_size=page_size)
    return ResponseModel.success(data=data)


@router.delete("/users/me/history/{history_id}", response_model=ResponseModel, summary="删除单条浏览历史")
async def delete_history(
    history_id: int,
    current_user: UserResponse = Depends(require_login),
):
    ok = await HistoryService.delete(history_id)
    if ok:
        await LogService.log(action="delete_history", operator=current_user, target_type="history", target_id=history_id)
    return ResponseModel.success(data={}, message="删除成功" if ok else "记录不存在")


@router.delete("/users/me/history/clear", response_model=ResponseModel, summary="清空浏览历史")
async def clear_history(
    current_user: UserResponse = Depends(require_login),
):
    count = await HistoryService.clear(current_user.id)
    if count:
        await LogService.log(action="clear_history", operator=current_user, target_type="history", target_id=0, detail={"count": count})
    return ResponseModel.success(data={"deleted_count": count}, message=f"已清空 {count} 条记录")
