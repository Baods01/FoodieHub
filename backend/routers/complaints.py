"""
complaints.py — 用户端反馈提交路由
"""

from fastapi import APIRouter, Depends

from schemas.common import ResponseModel
from schemas.users import UserResponse
from schemas.feedback import FeedbackCreateRequest
from services.feedback_service import FeedbackService
from utils.auth import require_login

router = APIRouter(prefix="/complaints", tags=["举报模块"])


@router.post("", response_model=ResponseModel, summary="提交举报")
async def create_complaint(
    data: FeedbackCreateRequest,
    current_user: UserResponse = Depends(require_login),
):
    result = await FeedbackService.create(current_user.id, data)
    return ResponseModel.success(data=result, message="反馈已提交")
