"""
log_dao.py — 统一操作日志数据访问层

对应 models/logs.py：OperationLog
职责：写入 + 查询，不跨表 JOIN，不提供修改/删除接口。
"""

from typing import Optional, List
from datetime import datetime
from models.logs import OperationLog


class LogDAO:
    """操作日志表 — OperationLog"""

    # ==================== 写入 ====================

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
    ) -> OperationLog:
        """
        记录一条操作日志。

        operator 接收以下类型：
        - Users 模型实例              → 完整 FK 关联
        - Pydantic UserResponse      → operator_id + operator_name
        - int（用户 ID）              → operator_id + 需调用方传入 operator_name
        - None                       → 系统自动操作
        """
        op_id = None
        op_name = operator_name
        if operator is not None:
            if isinstance(operator, int):
                op_id = operator
            elif hasattr(operator, "_saved_in_db"):
                # Tortoise ORM 模型实例 → 直接传 FK，Tortoise 自动处理
                op_name = op_name or getattr(operator, "username", None)
                return await OperationLog.create(
                    operator=operator,
                    operator_name=op_name,
                    action=action,
                    target_type=target_type,
                    target_id=target_id,
                    detail=detail,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    session_id=session_id,
                )
            else:
                # Pydantic 模型等 → 取 id 和 username
                op_id = getattr(operator, "id", None)
                op_name = op_name or getattr(operator, "username", None)

        return await OperationLog.create(
            operator_id=op_id,
            operator_name=op_name,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
        )

    # ==================== 查询 ====================

    @staticmethod
    async def get_by_id(id: int) -> Optional[OperationLog]:
        """按 ID 查询单条日志详情。"""
        return await OperationLog.get_or_none(id=id, is_active=True)

    @staticmethod
    async def list(
        action: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        operator_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        管理后台：按条件筛选日志列表，分页返回。

        返回格式：{"items": [...], "total": int, "page": int, "page_size": int}
        """
        qs = OperationLog.filter(is_active=True)

        if action:
            qs = qs.filter(action=action)
        if target_type:
            qs = qs.filter(target_type=target_type)
        if target_id is not None:
            qs = qs.filter(target_id=target_id)
        if operator_id is not None:
            qs = qs.filter(operator_id=operator_id)
        if start_time:
            qs = qs.filter(created_at__gte=start_time)
        if end_time:
            qs = qs.filter(created_at__lte=end_time)

        total = await qs.count()
        items = await qs.order_by("-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .prefetch_related("operator") \
            .all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_user_view_logs(
        user_id: int,
        action: str = "view_shop",
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        获取用户某类操作的历史记录（如浏览历史）。

        仅返回 OperationLog 记录本身，不跨表 JOIN。
        需要店铺名等信息的，由 Service 层组合 ShopDAO 查询。

        返回格式：{"items": [...], "total": int, "page": int, "page_size": int}
        """
        qs = OperationLog.filter(
            operator_id=user_id, action=action, is_active=True
        )

        total = await qs.count()
        items = await qs.order_by("-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    # ==================== 统计 ====================

    @staticmethod
    async def count_by_action(
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[dict]:
        """
        统计各操作类型的数量（管理后台仪表盘）。
        返回：[{"action": "view_shop", "count": 123}, ...]
        """
        from tortoise.functions import Count

        qs = OperationLog.filter(is_active=True)
        if start_time:
            qs = qs.filter(created_at__gte=start_time)
        if end_time:
            qs = qs.filter(created_at__lte=end_time)

        result = await qs.annotate(count=Count("id")) \
            .group_by("action") \
            .values("action", "count")
        # values() 不支持链式 order_by，Python 层排序
        result.sort(key=lambda x: -x.get("count", 0))
        return result
