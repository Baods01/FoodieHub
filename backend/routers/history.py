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
    """
    浏览历史接口
    
    查询参数:
    - page (integer, 可选): 页码，默认值为 1
    - page_size (integer, 可选): 每页大小，默认值为 20，最大值为 100
    
    响应:
    - 成功返回浏览历史记录
    - 失败返回错误信息
    """
    data = await HistoryService.get_view_history(current_user.id, page=page, page_size=page_size)
    return ResponseModel.success(data=data)


@router.delete("/users/me/history/{history_id}", response_model=ResponseModel, summary="删除单条浏览历史")
async def delete_history(
    history_id: int,
    current_user: UserResponse = Depends(require_login),
):
    """
    删除单条浏览历史接口
    
    路径参数:
    - history_id (integer, 必填): 浏览历史ID
    
    响应:
    - 成功返回删除成功信息
    - 失败返回错误信息
    """
    ok = await HistoryService.delete(history_id)
    if ok:
        await LogService.log(action="delete_history", operator=current_user, target_type="history", target_id=history_id)
    return ResponseModel.success(data={}, message="删除成功" if ok else "记录不存在")


@router.delete("/users/me/history/clear", response_model=ResponseModel, summary="清空浏览历史")
async def clear_history(
    current_user: UserResponse = Depends(require_login),
):
    """
    清空浏览历史接口
    
    响应:
    - 成功返回删除数量
    - 失败返回错误信息
    """
    count = await HistoryService.clear(current_user.id)
    if count:
        await LogService.log(action="clear_history", operator=current_user, target_type="history", target_id=0, detail={"count": count})
    return ResponseModel.success(data={"deleted_count": count}, message=f"已清空 {count} 条记录")
