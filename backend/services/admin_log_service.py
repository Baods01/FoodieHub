from typing import Optional, List, Dict, Any
from datetime import datetime
from dao.admin_log_dao import AdminLogDAO
from models.admin_logs import AdminOperationLog
from utils.logger import log_database_error, log_admin_operation
from utils.logger import log_database_error


class AdminLogService:
    """管理员操作日志服务类"""

    @classmethod
    async def create_admin_log(
        cls,
        operator_id: int,
        operator_account: str,
        operation_type: str,
        operation_module: str,
        operation_ip: str,
        target_object_id: Optional[int] = None,
        target_object_type: Optional[str] = None,
        before_snapshot: Optional[Dict] = None,
        after_snapshot: Optional[Dict] = None,
        operation_result: str = "success",
        operation_description: Optional[str] = None
    ) -> AdminOperationLog:
        """
        创建管理员操作日志
        
        Args:
            operator_id: 操作人ID
            operator_account: 操作人账号
            operation_type: 操作类型
            operation_module: 操作模块
            operation_ip: 操作IP
            target_object_id: 目标对象ID
            target_object_type: 目标对象类型
            before_snapshot: 操作前快照
            after_snapshot: 操作后快照
            operation_result: 操作结果
            operation_description: 操作描述
            
        Returns:
            创建的管理员日志对象
        """
        return await AdminLogDAO.create_admin_log(
            operator_id=operator_id,
            operator_account=operator_account,
            operation_type=operation_type,
            operation_module=operation_module,
            operation_ip=operation_ip,
            target_object_id=target_object_id,
            target_object_type=target_object_type,
            before_snapshot=before_snapshot,
            after_snapshot=after_snapshot,
            operation_result=operation_result,
            operation_description=operation_description
        )

    @classmethod
    async def get_admin_logs(
        cls,
        operator_id: Optional[int] = None,
        operation_module: Optional[str] = None,
        operation_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        target_object_type: Optional[str] = None,
        target_object_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        查询管理员操作日志
        
        Args:
            operator_id: 操作人ID
            operation_module: 操作模块
            operation_type: 操作类型
            start_time: 开始时间
            end_time: 结束时间
            target_object_type: 目标对象类型
            target_object_id: 目标对象ID
            page: 页码
            page_size: 每页大小
            
        Returns:
            包含日志列表和分页信息的字典
        """
        try:
            logs, total = await AdminLogDAO.get_admin_logs(
                operator_id=operator_id,
                operation_module=operation_module,
                operation_type=operation_type,
                start_time=start_time,
                end_time=end_time,
                target_object_type=target_object_type,
                target_object_id=target_object_id,
                page=page,
                page_size=page_size
            )
            
            # 转换为字典格式
            logs_data = []
            for log in logs:
                logs_data.append({
                    "id": log.id,
                    "operator_id": log.operator_id,
                    "operator_account": log.operator_account,
                    "operation_time": log.operation_time.isoformat() if log.operation_time else None,
                    "operation_ip": log.operation_ip,
                    "operation_type": log.operation_type,
                    "operation_module": log.operation_module,
                    "target_object_id": log.target_object_id,
                    "target_object_type": log.target_object_type,
                    "before_snapshot": log.before_snapshot,
                    "after_snapshot": log.after_snapshot,
                    "operation_result": log.operation_result,
                    "operation_description": log.operation_description,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                    "updated_at": log.updated_at.isoformat() if log.updated_at else None
                })
            
            return {
                "items": logs_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        except Exception as e:
            log_database_error("get_admin_logs", e, {
                "operator_id": operator_id,
                "operation_module": operation_module,
                "operation_type": operation_type,
                "page": page,
                "page_size": page_size
            })
            raise

    @classmethod
    async def export_admin_logs(
        cls,
        operator_id: Optional[int] = None,
        operation_module: Optional[str] = None,
        operation_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        target_object_type: Optional[str] = None,
        target_object_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
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
            
        Returns:
            日志数据列表
        """
        return await AdminLogDAO.export_admin_logs(
            operator_id=operator_id,
            operation_module=operation_module,
            operation_type=operation_type,
            start_time=start_time,
            end_time=end_time,
            target_object_type=target_object_type,
            target_object_id=target_object_id
        )

    @classmethod
    async def get_admin_log_by_id(cls, log_id: int) -> Optional[AdminOperationLog]:
        """
        根据ID获取管理员操作日志
        
        Args:
            log_id: 日志ID
            
        Returns:
            管理员日志对象或None
        """
        return await AdminLogDAO.get_admin_log_by_id(log_id)

    @classmethod
    async def delete_admin_log(cls, log_id: int) -> bool:
        """
        删除管理员操作日志
        
        Args:
            log_id: 日志ID
            
        Returns:
            是否删除成功
        """
        return await AdminLogDAO.delete_admin_log(log_id)