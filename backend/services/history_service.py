"""
history_service.py — 浏览历史业务逻辑

浏览历史（ViewHistory）是什么？
  用户在查看某个店铺详情时，系统自动记录一条浏览记录。
  这些记录在用户个人中心的"最近浏览"页面展示，方便用户回访。

浏览历史 vs 动态（Activities）的区别：
  - 浏览历史：用户"看"了哪些店铺（自动记录，量很大）
  - 动态：用户"做了"什么操作（评论/收藏/评分等，量较小）

生成方式：
  在 ShopService.get_by_id() 中，如果 user_id 不为空，
  会调用 ViewHistoryDAO.upsert() 记录一条浏览历史。
  upsert 的语义是"有则更新，无则插入"，保证同一用户同一店铺只有一条记录。

★ 关键设计：upsert（不存在则插入，存在则更新时间戳）
  ViewHistoryDAO.upsert(user_id, shop_id) 的逻辑：
  - 先查是否存在 user_id + shop_id 的记录
  - 如果存在，更新 viewed_at = NOW()
  - 如果不存在，创建新记录
  这种设计保证了：用户反复查看同一店铺时，不会产生多条重复记录，
  而是不断刷新"最近查看时间"，实现"最近浏览"的正确排序。

[教师可能问：为什么不用 REPLACE INTO 或 ON DUPLICATE KEY UPDATE？]
  答：Tortoise-ORM 不直接支持 MySQL 的 ON DUPLICATE KEY UPDATE 语法。
  用 get_or_none + save/create 是 ORM 层面的等价实现。
  虽然多了一次 SELECT 查询，但对于浏览历史这种低频写入（每次页面加载一次）来说，
  开销完全可接受。
"""

from typing import Optional
from dao.view_history_dao import ViewHistoryDAO
from dao.image_dao import ImageDAO


class HistoryService:
    """浏览历史业务逻辑"""

    @staticmethod
    async def get_view_history(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        获取当前用户的店铺浏览历史，附带店铺信息和封面图。

        返回格式：
        {
            "items": [
                {
                    "id": int,           # ViewHistory 记录 ID
                    "shop_id": int,       # 店铺 ID
                    "shop_name": str,     # 店铺名称（通过 FK 关联）
                    "shop_cover": str | None,  # 店铺封面图 URL（通过 ImageDAO 查）
                    "region": str | None,      # 预留字段，当前为 None
                    "viewed_at": str,     # 最近浏览时间（ISO 格式）
                },
            ],
            "total": int,
            "has_more": bool,   # ★ 自定义字段：是否还有更多数据
        }

        ★ 执行顺序说明：
          1. 调用 ViewHistoryDAO.list_by_user() 获取分页数据
             DAO 内部：
             - ViewHistory.filter(user_id=user_id, is_active=True)
             - .order_by("-viewed_at")  ← 按浏览时间降序（最新的在前）
             - .select_related("shop")  ← ★ JOIN shops 表，一次性查出店铺信息
             - offset/limit 分页
          2. 遍历每条记录：
             a. 通过关联的 shop 对象提取店铺名
             b. ★ 通过 ImageDAO.get_first_by_entity() 查店铺的封面图（多态关联）
             c. 手动序列化
          3. 计算 has_more（当前页 + 之前页的记录数 < 总记录数）
          4. 返回分页数据

        [教师可能问：这里的 has_more 为什么要手动计算，而不是用 total_pages？]
          答：前端的分页组件通常需要知道"还有没有下一页"来显示"加载更多"按钮。
          用 total_pages 需要再算一次 (total + page_size - 1) // page_size，
          而 has_more = offset + len(items) < total 更直观。

        ★ 潜在性能风险：
          for 循环中调用了 ImageDAO.get_first_by_entity("shop", item.shop_id)，
          如果一页有 20 条浏览记录，就会产生 20 次额外的 SELECT 查询。
          这是典型的 N+1 问题。改进方案：
          1. 在 DAO 层批量查询：先查出所有 shop_id，一次性查回所有封面图
          2. 在 Python 中用 dict(shop_id → cover_url) 做映射
          见 ShopService.search() 中已有类似的批量处理模式，可以借鉴。
        """
        result = await ViewHistoryDAO.list_by_user(user_id, page=page, page_size=page_size)
        items = result["items"]
        serialized = []
        for item in items:
            # ★ item.shop 通过 select_related("shop") 预加载
            # 如果没有 select_related，这里会触发 N+1
            shop = getattr(item, "shop", None)
            # ★ N+1 风险点：每条记录都查询一次 ImageDAO
            cover = await ImageDAO.get_first_by_entity("shop", item.shop_id) if shop else None
            serialized.append({
                "id": item.id,
                "shop_id": item.shop_id,
                "shop_name": shop.name if shop else "已删除的店铺",
                "shop_cover": cover.url if cover else None,
                "region": None,  # 预留字段，目前未实现
                "viewed_at": item.viewed_at.isoformat(),
            })
        return {
            "items": serialized,
            "total": result["total"],
            "has_more": len(items) + (page - 1) * page_size < result["total"],
        }

    @staticmethod
    async def delete(history_id: int) -> bool:
        """删除单条浏览历史（软删除）。"""
        return await ViewHistoryDAO.delete(history_id)

    @staticmethod
    async def clear(user_id: int) -> int:
        """清空用户所有浏览历史。返回受影响的行数。"""
        return await ViewHistoryDAO.clear_by_user(user_id)