from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from models.users import Users
from dependencies.auth import require_admin
from services.admin_log_service import AdminLogService

router = APIRouter(prefix="/admin/logs/test", tags=["测试管理员日志"])


@router.post("")
async def test_create_admin_log(
    operator_id: int,
    operator_account: str,
    operation_type: str,
    operation_module: str,
    operation_ip: str,
    operation_description: Optional[str] = None,
    current_user: Users = Depends(require_admin)
):
    """
    测试创建管理员日志
    
    Args:
        operator_id: 操作人ID
        operator_account: 操作人账号
        operation_type: 操作类型
        operation_module: 操作模块
        operation_ip: 操作IP
        operation_description: 操作描述
        current_user: 当前管理员用户
        
    Returns:
        创建结果
    """
    try:
        log = await AdminLogService.create_admin_log(
            operator_id=operator_id,
            operator_account=operator_account,
            operation_type=operation_type,
            operation_module=operation_module,
            operation_ip=operation_ip,
            operation_description=operation_description
        )
        return {"message": "日志创建成功", "log_id": log.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建日志失败: {str(e)}")