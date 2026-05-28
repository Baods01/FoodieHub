from typing import Optional
from datetime import datetime
from dao.log_dao import LogDAO
from dao.analytics_dao import AnalyticsDAO
from schemas.logs import LogResponse


class LogService:
    """操作日志业务逻辑"""

    @staticmethod
    async def log(
        action: str,
        operator=None,
        operator_name: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        detail: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """
        记录一条操作日志，作为业务操作的收尾步骤。
        Service 层在各个业务方法末尾调用此方法。
        """
        await LogDAO.log(
            action=action,
            operator=operator,
            operator_name=operator_name,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
        )

    @staticmethod
    async def get_logs(
        action: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        operator_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """管理员后台查看日志列表。"""
        return await LogDAO.list(
            action=action, target_type=target_type, target_id=target_id,
            operator_id=operator_id, start_time=start_time, end_time=end_time,
            page=page, page_size=page_size,
        )

    @staticmethod
    async def get_daily_trends(days: int = 7) -> list:
        """管理后台每日趋势。"""
        return await AnalyticsDAO.get_daily_trends(days=days)
