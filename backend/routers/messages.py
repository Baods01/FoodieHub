"""
消息通知路由 - FD03-07 查看消息通知

功能描述：已登录用户可在消息中心查看系统推送的所有互动通知。

功能需求：
- 通知类型包括：评论被回复、评论被点赞等
- 通知列表按时间倒序分页展示
- 未读通知有醒目的视觉标识
- 用户点击某条通知后，该条标记为已读并跳转至相关内容页
- 用户可点击"全部已读"一键标记所有未读通知为已读
- 也可单条删除或清空全部通知

业务规则：
- 消息来自 messages 表
- 未读数量从 messages 表计数（is_read=False）
- 点击通知后更新 is_read=True
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from schemas.common import ResponseModel, PaginationResponse, PaginationMeta, paginated_success
from schemas.messages import (
    MessageResponse,
    MessageMarkReadRequest,
    MessageDeleteRequest,
    UnreadCountResponse,
)
from models.users import Users
from dao.message_dao import MessageDAO
from dependencies.auth import get_current_user

router = APIRouter(prefix="/messages")


@router.get(
    "",
    response_model=ResponseModel[dict],
    summary="获取消息通知列表"
)
async def get_messages(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    unread_only: bool = Query(False, description="仅显示未读"),
    message_type: Optional[str] = Query(None, description="消息类型过滤"),
    current_user: Users = Depends(get_current_user)
):
    """
    获取当前用户的消息通知列表

    **查询参数**：
    - `page`: 页码（默认1）
    - `page_size`: 每页数量（默认20，最大100）
    - `unread_only`: 仅显示未读消息（默认false）
    - `message_type`: 消息类型过滤（如：comment_reply, like, mention, announcement）

    **业务规则**：
    - 消息按创建时间倒序排列
    - 支持分页查询
    - 仅返回 is_active=True 的消息
    - 消息内容经过敏感词过滤（已在创建时处理）

    **错误码**：
    - 401: 未登录
    """
    offset = (page - 1) * page_size

    messages = await MessageDAO.get_user_messages(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=page_size,
        offset=offset
    )

    total = await MessageDAO.get_unread_count(current_user.id) if unread_only else \
        await MessageDAO.get_user_messages_count(current_user.id, message_type)

    unread_count = await MessageDAO.get_unread_count(current_user.id)

    message_responses = [
        MessageResponse(
            id=msg.id,
            recipient_id=msg.recipient_id,
            sender={
                "id": msg.sender.id,
                "username": msg.sender.username,
                "avatar": msg.sender.avatar
            } if msg.sender else None,
            type=msg.type,
            title=msg.title,
            content=msg.content,
            related_entity_type=msg.related_entity_type,
            related_entity_id=msg.related_entity_id,
            is_read=msg.is_read,
            created_at=msg.created_at
        )
        for msg in messages
    ]

    return ResponseModel.success(data={
        "items": message_responses,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
        },
        "unread_count": unread_count
    })


@router.get(
    "/unread-count",
    response_model=ResponseModel[UnreadCountResponse],
    summary="获取未读消息数量"
)
async def get_unread_count(
    current_user: Users = Depends(get_current_user)
):
    """
    获取当前用户的未读消息数量

    **业务规则**：
    - 未读数量 = is_read=False 且 is_active=True 的消息总数
    - 用于在界面显示红点/badge

    **错误码**：
    - 401: 未登录
    """
    count = await MessageDAO.get_unread_count(current_user.id)
    return ResponseModel.success(data={"unread_count": count})


@router.post(
    "/mark-read",
    response_model=ResponseModel[dict],
    summary="标记消息为已读"
)
async def mark_messages_read(
    request: MessageMarkReadRequest,
    current_user: Users = Depends(get_current_user)
):
    """
    标记指定消息为已读

    **请求体**：
    - `message_ids`: 消息ID列表

    **业务规则**：
    - 仅能标记属于当前用户的消息
    - 已读消息的 is_read 设为 True
    - 支持批量标记

    **错误码**：
    - 401: 未登录
    - 400: 消息ID列表为空
    """
    if not request.message_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="消息ID列表不能为空"
        )

    marked_count = 0
    for message_id in request.message_ids:
        message = await MessageDAO.get_message_by_id(message_id)
        if message and message.recipient_id == current_user.id:
            if await MessageDAO.mark_message_as_read(message_id):
                marked_count += 1

    return ResponseModel.success(
        data={"marked_count": marked_count},
        message=f"已标记 {marked_count} 条消息为已读"
    )


@router.post(
    "/mark-all-read",
    response_model=ResponseModel[dict],
    summary="标记全部消息为已读"
)
async def mark_all_messages_read(
    current_user: Users = Depends(get_current_user)
):
    """
    标记当前用户所有未读消息为已读

    **业务规则**：
    - 将该用户所有 is_read=False 的消息更新为 is_read=True
    - 返回已标记的消息数量

    **错误码**：
    - 401: 未登录
    """
    marked_count = await MessageDAO.mark_all_messages_as_read(current_user.id)
    return ResponseModel.success(
        data={"marked_count": marked_count},
        message=f"已标记全部 {marked_count} 条消息为已读"
    )


@router.delete(
    "",
    response_model=ResponseModel[dict],
    summary="删除消息"
)
async def delete_messages(
    request: MessageDeleteRequest,
    current_user: Users = Depends(get_current_user)
):
    """
    删除指定消息（软删除）

    **请求体**：
    - `message_ids`: 消息ID列表

    **业务规则**：
    - 仅能删除属于当前用户的消息
    - 执行软删除（is_active=False）
    - 支持批量删除

    **错误码**：
    - 401: 未登录
    - 400: 消息ID列表为空
    """
    if not request.message_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="消息ID列表不能为空"
        )

    deleted_count = 0
    for message_id in request.message_ids:
        message = await MessageDAO.get_message_by_id(message_id)
        if message and message.recipient_id == current_user.id:
            if await MessageDAO.delete_message(message_id):
                deleted_count += 1

    return ResponseModel.success(
        data={"deleted_count": deleted_count},
        message=f"已删除 {deleted_count} 条消息"
    )


@router.delete(
    "/clear-all",
    response_model=ResponseModel[dict],
    summary="清空全部消息"
)
async def clear_all_messages(
    current_user: Users = Depends(get_current_user)
):
    """
    清空当前用户的所有消息（软删除）

    **业务规则**：
    - 将该用户所有消息的 is_active 设为 False
    - 返回已删除的消息数量
    - 这是危险操作，应在界面上有二次确认提示

    **错误码**：
    - 401: 未登录
    """
    deleted_count = await MessageDAO.delete_messages_by_user(current_user.id)
    return ResponseModel.success(
        data={"deleted_count": deleted_count},
        message=f"已清空全部 {deleted_count} 条消息"
    )


@router.get(
    "/{message_id}",
    response_model=ResponseModel[MessageResponse],
    summary="获取消息详情"
)
async def get_message_detail(
    message_id: int,
    current_user: Users = Depends(get_current_user)
):
    """
    获取消息详情，同时标记为已读

    **路径参数**：
    - `message_id`: 消息ID

    **业务规则**：
    - 仅能查看属于当前用户的消息
    - 调用此接口后，消息自动标记为已读
    - 返回消息详情，包含关联实体信息用于跳转

    **错误码**：
    - 401: 未登录
    - 404: 消息不存在或不属于当前用户
    """
    message = await MessageDAO.get_message_by_id(message_id)

    if not message or message.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )

    await MessageDAO.mark_message_as_read(message_id)

    return ResponseModel.success(data=MessageResponse(
        id=message.id,
        recipient_id=message.recipient_id,
        sender={
            "id": message.sender.id,
            "username": message.sender.username,
            "avatar": message.sender.avatar
        } if message.sender else None,
        type=message.type,
        title=message.title,
        content=message.content,
        related_entity_type=message.related_entity_type,
        related_entity_id=message.related_entity_id,
        is_read=True,
        created_at=message.created_at
    ))
