"""
log_service.py — 操作日志业务逻辑

操作日志（OperationLog）是什么？
  记录用户在平台上的"重要操作"行为，如删除店铺、封禁用户、修改权限等。
  这些日志用于：
  1. 管理员后台的审计追踪（谁在什么时候做了什么）
  2. 用户行为分析（统计每日活跃度等）

设计原则：
  - 日志是"追加写入"的，API 不提供删除/修改接口（已有的 delete 仅用于内部维护）
  - 每条日志在业务操作完成后记录（见 routers/ 中每个写操作末尾的 await LogService.log()）
  - operator_name 是冗余存储字段，即使用户被删除后，日志仍可追溯是谁操作的

调用链路（以删除店铺为例）：
  Router: DELETE /shops/{shop_id}
    → ShopService.delete(shop_id)       ← 先执行业务操作
    → LogService.log(action="delete_shop", ...)  ← 再记录日志（后置记录）

[教师可能问：为什么不把日志记录放在 Service 层内部，而是放在 Router 层？]
  答：这是一个有意的设计选择。把日志记录放在 Router 层意味着：
  - Service 层保持纯净，只关注业务逻辑
  - Router 层可以灵活决定"哪些操作需要记录日志"
  - 同一个 Service 方法在不同 Router 中被调用时，可以记录不同的 action 名称
  - 缺点：有可能忘记调 LogService.log()，造成日志遗漏

  [另一个角度] 也可以考虑在 Service 层统一记录，用装饰器 @log_action("delete_shop")
  自动捕获方法调用并记录日志，这样更不容易遗漏。
"""

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

        参数说明：
          action      : 操作动作名，如 "delete_shop"、"ban_user"、"approve_complaint"
          operator    : 操作用户对象（UserResponse 或 Users 模型实例），用于提取 id 和 name
          operator_name: 冗余的用户名（如果传了 operator，会自动从其提取 name）
          target_type : 操作对象类型，如 "shop"、"user"、"comment"
          target_id   : 操作对象 ID
          detail      : 额外的 JSON 详情，如 {"reason": "重复店铺", "before": {...}, "after": {...}}
          ip_address  : 客户端 IP（追踪来源）
          user_agent  : 客户端设备信息
          session_id  : 未登录用户的会话追踪

        ★ 调用链路：
          LogService.log(action="delete_shop", operator=current_user, target_type="shop", target_id=1)
            → LogDAO.log(action="delete_shop", operator_id=1, operator_name="admin", ...)
              → OperationLog.create(action="delete_shop", ...)
                → INSERT INTO operation_logs ...

        [教师可能问：detail 字段的 before/after 快照是怎么产生的？]
          答：目前在记录日志时，detail 由调用方手动构造。
          例如 record_log(action="ban_user", detail={"reason": "恶意刷屏"})。
          更完善的方案是在 DAO 层封装一个 log_with_snapshot() 方法，
          读取操作前和操作后的数据差异，自动生成 before/after 快照。
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
        """
        管理员后台查看日志列表（支持多维筛选和分页）。

        筛选条件都是可选的，不传就查全部：
        - action="delete_shop"  → 只查删除店铺的日志
        - operator_id=1         → 只查用户 1 的操作日志
        - start_time/end_time   → 查某个时间范围内的日志

        ★ 返回结果中的 operator_name 处理策略：
          优先使用 OperationLog 表中的冗余字段 operator_name，
          如果冗余字段为空（历史数据），则通过 FK 关联查询 Users 表获取用户名。
          这种"冗余优先+FK 兜底"的模式兼容了新老数据。

        [教师可能问：operator_name 冗余存储会不会导致数据不一致？]
          答：确实存在风险——如果用户改名了，旧的日志记录仍然是旧的用户名。
          但这是有意为之的：日志的职责是"记录当时发生了什么"，
          如果用户后来改了名，旧日志保留旧名字才是正确的行为。
          如果需要"当前用户名"，可以通过 FK 关联 Users 表实时获取。
        """
        result = await LogDAO.list(
            action=action, target_type=target_type, target_id=target_id,
            operator_id=operator_id, start_time=start_time, end_time=end_time,
            page=page, page_size=page_size,
        )
        items = []
        for log in result["items"]:
            # operator_name 优先用冗余字段，否则从 FK 关联取
            op_name = log.operator_name
            if not op_name and log.operator_id:
                # ★ 这里 await log.operator 会触发一次 FK 查询
                # 如果大量日志都缺失 operator_name，会导致 N+1 查询
                # 但正常情况下冗余字段都有值，所以这个查询很少触发
                op_user = await log.operator
                op_name = op_user.username if op_user else None
            items.append({
                "id": log.id,
                "operator_name": op_name,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "detail": log.detail,
                "created_at": log.created_at.isoformat(),
            })
        return {"items": items, "total": result["total"], "page": result["page"], "page_size": result["page_size"]}

    @staticmethod
    async def get_daily_trends(days: int = 7) -> list:
        """管理后台每日趋势。透传调用 AnalyticsDAO。"""
        return await AnalyticsDAO.get_daily_trends(days=days)