from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from schemas.common import ResponseModel
from schemas.users import UserResponse
from schemas.interaction import (
    CommentCreate, QuestionCreate, LikeToggleRequest,
)
from services import CommentService, QuestionService, LogService
from services.like_service import LikeService
from utils.auth import get_current_user, require_login

router = APIRouter(tags=["互动模块"])


# ==================== 一级评论 ====================

@router.post("/shops/{shop_id}/comments", response_model=ResponseModel, summary="发表评论")
async def create_comment(
    shop_id: int,
    data: CommentCreate,
    current_user: UserResponse = Depends(require_login),
):
    result = await CommentService.create(shop_id, current_user.id, data.content, data.image_id)
    await LogService.log(action="create_comment", operator=current_user, target_type="shop", target_id=shop_id)
    return ResponseModel.success(data=result, message="评论成功")


@router.get("/shops/{shop_id}/comments", response_model=ResponseModel, summary="评论列表")
async def list_comments(
    shop_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
):
    uid = current_user.id if current_user else None
    result = await CommentService.list_by_shop(shop_id, page=page, page_size=page_size, user_id=uid)
    return ResponseModel.success(data=result, message="获取成功")


@router.put("/comments/{comment_id}", response_model=ResponseModel, summary="更新评论")
async def update_comment(
    comment_id: int,
    data: CommentCreate,
    current_user: UserResponse = Depends(require_login),
):
    result = await CommentService.update(comment_id, data.content)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    await LogService.log(action="update_comment", operator=current_user, target_type="comment", target_id=comment_id)
    return ResponseModel.success(data=result, message="更新成功")


@router.delete("/comments/{comment_id}", response_model=ResponseModel, summary="删除评论")
async def delete_comment(comment_id: int, current_user: UserResponse = Depends(require_login)):
    ok = await CommentService.delete(comment_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    await LogService.log(action="delete_comment", operator=current_user, target_type="comment", target_id=comment_id)
    return ResponseModel.success(data={}, message="删除成功")


# ==================== 二级回复 ====================

@router.post("/comments/{comment_id}/replies", response_model=ResponseModel, summary="回复评论")
async def create_reply(
    comment_id: int,
    content: str = Query(..., min_length=1),
    reply_to_user_id: Optional[int] = Query(None),
    current_user: UserResponse = Depends(require_login),
):
    result = await CommentService.create_reply(
        comment_id, current_user.id, content,
        reply_to_user_id=reply_to_user_id,
    )
    # 通知评论作者
    from dao.comment_dao import CommentDAO
    from services.message_service import MessageService
    comment = await CommentDAO.get_by_id(comment_id)
    if comment and comment.user_id != current_user.id:
        await MessageService.create_notification(
            recipient_id=comment.user_id,
            sender_id=current_user.id,
            type="reply_comment",
            title="新回复",
            content=f"{current_user.username} 回复了你的评论",
            related_entity_type="shop",
            related_entity_id=comment.shop_id,
        )
    await LogService.log(action="create_reply", operator=current_user, target_type="comment", target_id=comment_id)
    return ResponseModel.success(data=result, message="回复成功")


@router.get("/comments/{comment_id}/replies", response_model=ResponseModel, summary="回复列表")
async def list_replies(comment_id: int, current_user: UserResponse = Depends(get_current_user)):
    uid = current_user.id if current_user else None
    items = await CommentService.list_replies(comment_id, user_id=uid)
    return ResponseModel.success(data=items, message="获取成功")


@router.delete("/replies/{reply_id}", response_model=ResponseModel, summary="删除回复")
async def delete_reply(reply_id: int, current_user: UserResponse = Depends(require_login)):
    ok = await CommentService.delete_reply(reply_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="回复不存在")
    await LogService.log(action="delete_reply", operator=current_user, target_type="reply", target_id=reply_id)
    return ResponseModel.success(data={}, message="删除成功")


# ==================== 一级问题 ====================

@router.post("/shops/{shop_id}/questions", response_model=ResponseModel, summary="提问")
async def create_question(
    shop_id: int,
    title: str = Query(..., min_length=1),
    content: Optional[str] = Query(None),
    current_user: UserResponse = Depends(require_login),
):
    result = await QuestionService.create(shop_id, current_user.id, title, content=content)
    await LogService.log(action="create_question", operator=current_user, target_type="shop", target_id=shop_id)
    return ResponseModel.success(data=result, message="提问成功")


@router.get("/shops/{shop_id}/questions", response_model=ResponseModel, summary="问题列表")
async def list_questions(
    shop_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
):
    uid = current_user.id if current_user else None
    result = await QuestionService.list_by_shop(shop_id, page=page, page_size=page_size, user_id=uid)
    return ResponseModel.success(data=result, message="获取成功")


@router.put("/questions/{question_id}", response_model=ResponseModel, summary="更新问题")
async def update_question(
    question_id: int,
    data: QuestionCreate,
    current_user: UserResponse = Depends(require_login),
):
    result = await QuestionService.update(question_id, title=data.title, content=data.content)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")
    return ResponseModel.success(data=result, message="更新成功")


@router.delete("/questions/{question_id}", response_model=ResponseModel, summary="删除问题")
async def delete_question(question_id: int, current_user: UserResponse = Depends(require_login)):
    ok = await QuestionService.delete(question_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")
    await LogService.log(action="delete_question", operator=current_user, target_type="question", target_id=question_id)
    return ResponseModel.success(data={}, message="删除成功")


# ==================== 二级回答 ====================

@router.post("/questions/{question_id}/answers", response_model=ResponseModel, summary="回答")
async def create_answer(
    question_id: int,
    content: str = Query(..., min_length=1),
    reply_to_user_id: Optional[int] = Query(None),
    current_user: UserResponse = Depends(require_login),
):
    result = await QuestionService.create_answer(
        question_id, current_user.id, content,
        reply_to_user_id=reply_to_user_id,
    )
    # 通知提问作者
    from dao.question_dao import QuestionDAO
    from services.message_service import MessageService
    question = await QuestionDAO.get_by_id(question_id)
    if question and question.user_id != current_user.id:
        await MessageService.create_notification(
            recipient_id=question.user_id,
            sender_id=current_user.id,
            type="reply_answer",
            title="新回答",
            content=f"{current_user.username} 回答了你的问题",
            related_entity_type="shop",
            related_entity_id=question.shop_id,
        )
    await LogService.log(action="create_answer", operator=current_user, target_type="question", target_id=question_id)
    return ResponseModel.success(data=result, message="回答成功")


@router.get("/questions/{question_id}/answers", response_model=ResponseModel, summary="回答列表")
async def list_answers(question_id: int, current_user: UserResponse = Depends(get_current_user)):
    uid = current_user.id if current_user else None
    items = await QuestionService.list_answers(question_id, user_id=uid)
    return ResponseModel.success(data=items, message="获取成功")


@router.delete("/answers/{answer_id}", response_model=ResponseModel, summary="删除回答")
async def delete_answer(answer_id: int, current_user: UserResponse = Depends(require_login)):
    ok = await QuestionService.delete_answer(answer_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="回答不存在")
    await LogService.log(action="delete_answer", operator=current_user, target_type="answer", target_id=answer_id)
    return ResponseModel.success(data={}, message="删除成功")


# ==================== 点赞 ====================

@router.post("/likes/toggle", response_model=ResponseModel, summary="切换点赞")
async def toggle_like(
    data: LikeToggleRequest,
    current_user: UserResponse = Depends(require_login),
):
    try:
        result = await LikeService.toggle(current_user.id, data.entity_type, data.entity_id)
        # 点赞时通知内容作者
        if result.get("is_liked") and data.entity_type in ("shop_comment", "comment_reply", "shop_question", "question_answer"):
            from services.message_service import MessageService
            recipient_id = None
            shop_id = None
            if data.entity_type == "shop_comment":
                from dao.comment_dao import CommentDAO
                entity = await CommentDAO.get_by_id(data.entity_id)
                recipient_id = entity.user_id if entity else None
                shop_id = entity.shop_id if entity else None
            elif data.entity_type == "comment_reply":
                from dao.comment_dao import CommentDAO
                entity = await CommentDAO.get_reply_by_id(data.entity_id)
                recipient_id = entity.user_id if entity else None
                if entity:
                    comment = await CommentDAO.get_by_id(entity.comment_id)
                    shop_id = comment.shop_id if comment else None
            elif data.entity_type == "shop_question":
                from dao.question_dao import QuestionDAO
                entity = await QuestionDAO.get_by_id(data.entity_id)
                recipient_id = entity.user_id if entity else None
                shop_id = entity.shop_id if entity else None
            elif data.entity_type == "question_answer":
                from dao.question_dao import QuestionDAO
                entity = await QuestionDAO.get_answer_by_id(data.entity_id)
                recipient_id = entity.user_id if entity else None
                if entity:
                    question = await QuestionDAO.get_by_id(entity.question_id)
                    shop_id = question.shop_id if question else None
            if recipient_id and recipient_id != current_user.id and shop_id:
                notif_type = "like_comment" if data.entity_type in ("shop_comment", "comment_reply") else "like_answer"
                await MessageService.create_notification(
                    recipient_id=recipient_id,
                    sender_id=current_user.id,
                    type=notif_type,
                    title="新的赞",
                    content=f"{current_user.username} 赞了你的内容",
                    related_entity_type="shop",
                    related_entity_id=shop_id,
                )
        await LogService.log(action="toggle_like", operator=current_user, target_type=data.entity_type, target_id=data.entity_id)
        return ResponseModel.success(data=result, message="操作成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
