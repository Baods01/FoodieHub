from typing import Optional, List, Dict, Any
from models.admin_logs import AdminOperationLog
from datetime import datetime
from utils.logger import log_database_error
from utils.logger import log_database_error


class AdminLogDAO:
    """管理员操作日志数据访问对象"""

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
        try:
            log = await AdminOperationLog.create(
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
            return log
        except Exception as e:
            log_database_error("create_admin_log", e, {
                "operator_id": operator_id,
                "operation_type": operation_type,
                "operation_module": operation_module
            })
            raise

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
    ) -> tuple[List[AdminOperationLog], int]:
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
            (日志列表, 总数)
        """
        query = AdminOperationLog.all()
        
        # 添加筛选条件
        if operator_id is not None:
            query = query.filter(operator_id=operator_id)
        if operation_module:
            query = query.filter(operation_module=operation_module)
        if operation_type:
            query = query.filter(operation_type=operation_type)
        if start_time:
            query = query.filter(operation_time__gte=start_time)
        if end_time:
            query = query.filter(operation_time__lte=end_time)
        if target_object_type:
            query = query.filter(target_object_type=target_object_type)
        if target_object_id is not None:
            query = query.filter(target_object_id=target_object_id)
            
        # 按时间倒序排列
        query = query.order_by("-operation_time")
        
        # 分页处理
        offset = (page - 1) * page_size
        logs = await query.offset(offset).limit(page_size).all()
        
        # 获取总数
        total = await query.count()
        
        return logs, total

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
        query = AdminOperationLog.all()
        
        # 添加筛选条件
        if operator_id is not None:
            query = query.filter(operator_id=operator_id)
        if operation_module:
            query = query.filter(operation_module=operation_module)
        if operation_type:
            query = query.filter(operation_type=operation_type)
        if start_time:
            query = query.filter(operation_time__gte=start_time)
        if end_time:
            query = query.filter(operation_time__lte=end_time)
        if target_object_type:
            query = query.filter(target_object_type=target_object_type)
        if target_object_id is not None:
            query = query.filter(target_object_id=target_object_id)
            
        # 按时间倒序排列
        query = query.order_by("-operation_time")
        
        # 转换为字典格式
        logs = await query.all()
        return [
            {
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
            }
            for log in logs
        ]

    @classmethod
    async def get_admin_log_by_id(cls, log_id: int) -> Optional[AdminOperationLog]:
        """
        根据ID获取管理员操作日志
        
        Args:
            log_id: 日志ID
            
        Returns:
            管理员日志对象或None
        """
        return await AdminOperationLog.get_or_none(id=log_id)

    @classmethod
    async def delete_admin_log(cls, log_id: int) -> bool:
        """
        删除管理员操作日志
        
        Args:
            log_id: 日志ID
            
        Returns:
            是否删除成功
        """
        deleted_count = await AdminOperationLog.filter(id=log_id).delete()
        return deleted_count > 0