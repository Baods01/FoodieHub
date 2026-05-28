from fastapi import APIRouter, Depends, Query

from schemas.common import ResponseModel
from schemas.users import UserResponse
from dao.log_dao import LogDAO
from utils.auth import require_login

router = APIRouter(tags=["浏览历史模块"])


@router.get("/users/me/history", response_model=ResponseModel, summary="浏览历史")
async def get_my_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_login),
):
    """当前用户的店铺浏览历史。"""
    data = await LogDAO.get_user_view_logs(current_user.id, action="view_shop", page=page, page_size=page_size)
    return ResponseModel.success(data=data)
