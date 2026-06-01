"""
complaints.py — 用户端反馈提交路由
"""

from fastapi import APIRouter, Depends

from schemas.common import ResponseModel
from schemas.users import UserResponse
from schemas.feedback import FeedbackCreateRequest
from services import LogService
from services.feedback_service import FeedbackService
from utils.auth import require_login

router = APIRouter(prefix="/complaints", tags=["举报模块"])


@router.post("", response_model=ResponseModel, summary="提交举报")
async def create_complaint(
    data: FeedbackCreateRequest,
    current_user: UserResponse = Depends(require_login),
):
    """
    提交举报接口
    
    请求参数 (FeedbackCreateRequest):
    - type (string, 必填): 类型，可选值为 "complaint"（举报）或 "edit_request"（勘误）
    - target_type (string, 必填): 目标类型，可选值为 "shop"、"comment"、"image"
    - target_id (integer, 必填): 被反馈对象ID
    - reason_id (integer, 必填): 反馈原因ID（来自 dict_data）
    - description (string, 可选): 补充说明，最大1000字符
    
    响应:
    - 成功返回反馈信息
    - 失败返回错误信息
    """
    result = await FeedbackService.create(current_user.id, data)
    await LogService.log(action="create_feedback", operator=current_user, target_type=data.target_type, target_id=data.target_id, detail={"type": data.type})
    return ResponseModel.success(data=result, message="反馈已提交")
