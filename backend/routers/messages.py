from fastapi import APIRouter, Depends, HTTPException, status, Query

from schemas.common import ResponseModel
from schemas.users import UserResponse
from schemas.messages import MessageMarkReadRequest, MessageDeleteRequest
from services import MessageService
from utils.auth import require_login

router = APIRouter(prefix="/messages", tags=["消息通知模块"])


@router.get("", response_model=ResponseModel, summary="消息列表")
async def list_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    type: str = Query(None),
    current_user: UserResponse = Depends(require_login),
):
    result = await MessageService.list(
        current_user.id, unread_only=unread_only,
        type=type, page=page, page_size=page_size,
    )
    return ResponseModel.success(data=result, message="获取成功")


@router.get("/unread-count", response_model=ResponseModel, summary="未读数")
async def get_unread_count(current_user: UserResponse = Depends(require_login)):
    count = await MessageService.get_unread_count(current_user.id)
    return ResponseModel.success(data={"unread_count": count})


@router.post("/mark-read", response_model=ResponseModel, summary="标记已读")
async def mark_read(
    data: MessageMarkReadRequest,
    current_user: UserResponse = Depends(require_login),
):
    marked = await MessageService.mark_read(current_user.id, data.message_ids)
    return ResponseModel.success(data={"marked_count": marked}, message="操作成功")


@router.post("/mark-all-read", response_model=ResponseModel, summary="全部已读")
async def mark_all_read(current_user: UserResponse = Depends(require_login)):
    marked = await MessageService.mark_all_read(current_user.id)
    return ResponseModel.success(data={"marked_count": marked}, message="操作成功")


@router.delete("", response_model=ResponseModel, summary="删除消息")
async def delete_messages(
    data: MessageDeleteRequest,
    current_user: UserResponse = Depends(require_login),
):
    deleted = await MessageService.delete_messages(current_user.id, data.message_ids)
    return ResponseModel.success(data={"deleted_count": deleted}, message="删除成功")


@router.delete("/clear-all", response_model=ResponseModel, summary="清空消息")
async def clear_all(current_user: UserResponse = Depends(require_login)):
    deleted = await MessageService.clear(current_user.id)
    return ResponseModel.success(data={"deleted_count": deleted}, message="已清空")
