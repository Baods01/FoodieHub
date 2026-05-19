from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from schemas.admin_logs import (
    AdminLogQueryParams, AdminLogResponse, AdminLogExportResponse
)
from services.admin_log_service import AdminLogService
from dependencies.auth import require_admin
from models.users import Users
from utils.logger import log_database_error, log_admin_operation


router = APIRouter(prefix="/admin/logs")


@router.get("", response_model=AdminLogResponse)
async def get_admin_logs(
    params: AdminLogQueryParams = Depends(),
    current_user: Users = Depends(require_admin)
):
    """
    查询管理员操作日志
    
    Args:
        params: 查询参数
        current_user: 当前管理员用户
        
    Returns:
        日志列表和分页信息
    """
    try:
        result = await AdminLogService.get_admin_logs(
            operator_id=params.operator_id,
            operation_module=params.operation_module,
            operation_type=params.operation_type,
            start_time=params.start_time,
            end_time=params.end_time,
            target_object_type=params.target_object_type,
            target_object_id=params.target_object_id,
            page=params.page,
            page_size=params.page_size
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询日志失败: {str(e)}")


@router.get("/export", response_model=List[AdminLogExportResponse])
async def export_admin_logs(
    operator_id: Optional[int] = Query(None, description="操作人ID"),
    operation_module: Optional[str] = Query(None, description="操作模块"),
    operation_type: Optional[str] = Query(None, description="操作类型"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    target_object_type: Optional[str] = Query(None, description="目标对象类型"),
    target_object_id: Optional[int] = Query(None, description="目标对象ID"),
    current_user: Users = Depends(require_admin)
):
    """
    导出管理员操作日志
    
    Args:
        operator_id: 操作人ID
        operation_module: 操作模块
        operation_type: 操作类型
        start_time: 开始时间
        end_time: 结束时间
        target_object_type: 目标对象类型
        target_object_id: 目标对象ID
        current_user: 当前管理员用户
        
    Returns:
        日志数据列表
    """
    try:
        result = await AdminLogService.export_admin_logs(
            operator_id=operator_id,
            operation_module=operation_module,
            operation_type=operation_type,
            start_time=start_time,
            end_time=end_time,
            target_object_type=target_object_type,
            target_object_id=target_object_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出日志失败: {str(e)}")


@router.delete("/{log_id}")
async def delete_admin_log(
    log_id: int,
    current_user: Users = Depends(require_admin)
):
    """
    删除管理员操作日志
    
    Args:
        log_id: 日志ID
        current_user: 当前管理员用户
        
    Returns:
        删除结果
    """
    try:
        success = await AdminLogService.delete_admin_log(log_id)
        if not success:
            raise HTTPException(status_code=404, detail="日志记录不存在")
        return {"message": "删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除日志失败: {str(e)}")