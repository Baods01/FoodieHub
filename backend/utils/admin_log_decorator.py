from functools import wraps
from typing import Callable, Any
import json
from datetime import datetime
from services.admin_log_service import AdminLogService
from utils.logger import log_database_error


def log_admin_operation(
    operation_type: str,
    operation_module: str,
    target_object_type: str = None,
    operation_description: str = None
):
    """
    管理员操作日志装饰器
    
    Args:
        operation_type: 操作类型 (create, update, delete, approve, reject, etc.)
        operation_module: 操作模块 (user, shop, comment, etc.)
        target_object_type: 目标对象类型
        operation_description: 操作描述
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 获取当前用户信息（假设第一个参数是当前用户）
            current_user = None
            if args and hasattr(args[0], 'current_user'):
                current_user = args[0].current_user
            elif 'current_user' in kwargs:
                current_user = kwargs['current_user']
            
            # 获取操作IP（需要从请求上下文中获取）
            operation_ip = "unknown"
            if args and hasattr(args[0], 'request'):
                operation_ip = args[0].request.client.host
            
            # 记录操作前的状态
            before_snapshot = None
            
            try:
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 记录操作后的状态
                after_snapshot = None
                if hasattr(result, '__dict__'):
                    after_snapshot = result.__dict__
                elif isinstance(result, dict):
                    after_snapshot = result
                    
                # 创建日志记录
                if current_user:
                    try:
                        await AdminLogService.create_admin_log(
                            operator_id=current_user.id,
                            operator_account=current_user.username,
                            operation_type=operation_type,
                            operation_module=operation_module,
                            operation_ip=operation_ip,
                            target_object_id=getattr(result, 'id', None) if hasattr(result, 'id') else None,
                            target_object_type=target_object_type,
                            before_snapshot=before_snapshot,
                            after_snapshot=after_snapshot,
                            operation_result="success",
                            operation_description=operation_description or f"{operation_type} {target_object_type}"
                        )
                    except Exception as log_error:
                        # 即使日志记录失败也不影响主流程，但要记录错误
                        from utils.logger import log_admin_operation_error
                        log_admin_operation_error("create_admin_log", log_error, {
                            "operator_id": current_user.id,
                            "operation_type": operation_type,
                            "operation_module": operation_module,
                            "error": str(log_error)
                        })
                
                return result
                
            except Exception as e:
                # 记录失败的操作
                if current_user:
                    try:
                        await AdminLogService.create_admin_log(
                            operator_id=current_user.id,
                            operator_account=current_user.username,
                            operation_type=operation_type,
                            operation_module=operation_module,
                            operation_ip=operation_ip,
                            target_object_id=None,
                            target_object_type=target_object_type,
                            before_snapshot=before_snapshot,
                            after_snapshot=None,
                            operation_result="failed",
                            operation_description=operation_description or f"{operation_type} {target_object_type} failed: {str(e)}"
                        )
                    except Exception as log_error:
                        # 即使日志记录失败也不影响主流程，但要记录错误
                        from utils.logger import log_admin_operation_error
                        log_admin_operation_error("create_admin_log_failed", log_error, {
                            "operator_id": current_user.id,
                            "operation_type": operation_type,
                            "operation_module": operation_module,
                            "error": str(log_error)
                        })
                raise
                
        return wrapper
    return decorator
