from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from schemas.common import ResponseModel
from schemas.users import UserResponse
from schemas.interaction import (
    CommentCreate, LikeToggleRequest,
)
from services import CommentService, QuestionService
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
    result = await CommentService.create(shop_id, current_user.id, data.content)
    return ResponseModel.success(data=result, message="评论成功")


@router.get("/shops/{shop_id}/comments", response_model=ResponseModel, summary="评论列表")
async def list_comments(
    shop_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
):
    result = await CommentService.list_by_shop(shop_id, page=page, page_size=page_size)
    return ResponseModel.success(data=result, message="获取成功")


@router.put("/comments/{comment_id}", response_model=ResponseModel, summary="更新评论")
async def update_comment(
    comment_id: int,
    content: str = Query(..., min_length=1),
    current_user: UserResponse = Depends(require_login),
):
    result = await CommentService.update(comment_id, content)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    return ResponseModel.success(data=result, message="更新成功")


@router.delete("/comments/{comment_id}", response_model=ResponseModel, summary="删除评论")
async def delete_comment(comment_id: int, current_user: UserResponse = Depends(require_login)):
    ok = await CommentService.delete(comment_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
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
    return ResponseModel.success(data=result, message="回复成功")


@router.get("/comments/{comment_id}/replies", response_model=ResponseModel, summary="回复列表")
async def list_replies(comment_id: int, current_user: UserResponse = Depends(get_current_user)):
    items = await CommentService.list_replies(comment_id)
    return ResponseModel.success(data=items, message="获取成功")


@router.delete("/replies/{reply_id}", response_model=ResponseModel, summary="删除回复")
async def delete_reply(reply_id: int, current_user: UserResponse = Depends(require_login)):
    ok = await CommentService.delete_reply(reply_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="回复不存在")
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
    return ResponseModel.success(data=result, message="提问成功")


@router.get("/shops/{shop_id}/questions", response_model=ResponseModel, summary="问题列表")
async def list_questions(
    shop_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
):
    result = await QuestionService.list_by_shop(shop_id, page=page, page_size=page_size)
    return ResponseModel.success(data=result, message="获取成功")


@router.put("/questions/{question_id}", response_model=ResponseModel, summary="更新问题")
async def update_question(
    question_id: int,
    title: Optional[str] = Query(None),
    content: Optional[str] = Query(None),
    current_user: UserResponse = Depends(require_login),
):
    result = await QuestionService.update(question_id, title=title, content=content)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")
    return ResponseModel.success(data=result, message="更新成功")


@router.delete("/questions/{question_id}", response_model=ResponseModel, summary="删除问题")
async def delete_question(question_id: int, current_user: UserResponse = Depends(require_login)):
    ok = await QuestionService.delete(question_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")
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
    return ResponseModel.success(data=result, message="回答成功")


@router.get("/questions/{question_id}/answers", response_model=ResponseModel, summary="回答列表")
async def list_answers(question_id: int, current_user: UserResponse = Depends(get_current_user)):
    items = await QuestionService.list_answers(question_id)
    return ResponseModel.success(data=items, message="获取成功")


@router.delete("/answers/{answer_id}", response_model=ResponseModel, summary="删除回答")
async def delete_answer(answer_id: int, current_user: UserResponse = Depends(require_login)):
    ok = await QuestionService.delete_answer(answer_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="回答不存在")
    return ResponseModel.success(data={}, message="删除成功")


# ==================== 点赞 ====================

@router.post("/likes/toggle", response_model=ResponseModel, summary="切换点赞")
async def toggle_like(
    data: LikeToggleRequest,
    current_user: UserResponse = Depends(require_login),
):
    try:
        result = await LikeService.toggle(current_user.id, data.entity_type, data.entity_id)
        return ResponseModel.success(data=result, message="操作成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
