"""
analytics_service.py — 统计分析业务逻辑

该 Service 负责管理后台的数据看板接口。
所有方法都是"透传"（passthrough）模式：
Service 层不做任何业务处理，直接调用 AnalyticsDAO 的方法并原样返回结果。

设计意图：
  统计分析本质上是"读密集型"操作，DAO 层负责编写聚合 SQL 来汇总数据，
  Service 层只做方法路由。这样当统计逻辑变化时（比如从 SQL 聚合改为
  Redis 缓存），只需要改 AnalyticsDAO，Service 层保持稳定。

调用链路：
  Router（routers/admin.py）
    → AnalyticsService.get_overview()
      → AnalyticsDAO.get_overview()       ← 在 dao/analytics_dao.py 中执行聚合 SQL
        → Tortoise ORM execute_query()    ← 执行原生 SQL 查询

[教师可能问：为什么不做分层缓存？]
  答：目前每次刷新页面都重新查询数据库，对于日活 500 以内的校园应用是可接受的。
  如果未来需要优化，可以在 AnalyticsDAO 层加 Redis 缓存，key 按聚合维度设置过期时间。
"""

from dao.analytics_dao import AnalyticsDAO
from dao.dict_dao import DictDataDAO


class AnalyticsService:
    """统计分析业务逻辑"""

    @staticmethod
    async def get_overview() -> dict:
        """
        获取全站概览数据。

        包括：用户总数、店铺总数、评论总数、待处理举报数等核心指标。
        实际聚合逻辑在 AnalyticsDAO.get_overview() 中通过多条 SELECT COUNT 实现。

        返回示例：
        {
            "total_users": 1024,
            "total_shops": 256,
            "total_comments": 8192,
            "pending_complaints": 3,
        }
        """
        return await AnalyticsDAO.get_overview()

    @staticmethod
    async def get_daily_trends(days: int = 7) -> list:
        """
        获取每日新增用户和店铺的趋势数据。

        参数 days：回溯天数，默认 7 天。
        返回按日期分组的 [{date: "2026-06-07", new_users: 5, new_shops: 1}, ...]。
        """
        return await AnalyticsDAO.get_daily_trends(days)

    @staticmethod
    async def get_shop_category_distribution() -> list:
        """
        品类分布：取"品类"字典类型的所有数据项，统计各标签店铺数。

        ★ 调用链路（跨两个 DAO）：
          步骤 1: DictDataDAO.get_by_type_name("品类")
            → 从 dict_data 表中查出所有"品类"标签（如：中餐、西餐、日料...）
            → 对应 models/dict.py 中的 DictData 模型，filter by type_name

          步骤 2: AnalyticsDAO.count_shops_by_dict_data(ids)
            → 对每个 ID 执行 SELECT COUNT(*) FROM dict_rel WHERE entity_type='shop' AND dict_data_id=?
            → 返回 [{dict_data_id: 1, count: 42}, ...]

        [教师可能问：为什么不在一个 SQL 里用 JOIN 完成？]
          答：可以，但分两步更清晰：
          - 第一步是"查询字典"（独立的业务概念）
          - 第二步是"统计关联"（独立的统计概念）
          拆开有利于维护，且字典数据通常会被缓存，不需要每次都 JOIN。
        """
        # 第一步：查出所有"品类"标签的 ID 和名称
        cat_items = await DictDataDAO.get_by_type_name("品类")
        ids = [item.id for item in cat_items]
        # 第二步：统计每个品类标签关联了多少家店铺
        return await AnalyticsDAO.count_shops_by_dict_data(ids)

    @staticmethod
    async def get_top_rated_shops(limit: int = 10) -> list:
        """
        获取评分最高的 N 家店铺（默认取前 10）。

        排序依据：Shops.average_rating 降序。
        该字段是冗余字段，在每次评分操作后被同步更新（见 shops_dao.py 的 _recalc_average_rating）。

        [教师可能问：如果两张表评分一样怎么处理？]
          答：当前实现只按 average_rating DESC 排序，评分相同时顺序不确定。
          规范化做法是加二级排序 ORDER BY average_rating DESC, comment_count DESC。
        """
        return await AnalyticsDAO.get_top_rated_shops(limit)

    @staticmethod
    async def get_most_favorited_shops(limit: int = 10) -> list:
        """
        获取收藏数最多的 N 家店铺（默认取前 10）。

        排序依据：Shops.favorite_count 降序。
        该字段是冗余字段，由 ShopsDAO.sync_favorite_count() 维护。
        """
        return await AnalyticsDAO.get_most_favorited_shops(limit)

    @staticmethod
    async def get_pending_counts() -> dict:
        """
        获取待处理事项的计数（用于管理员首页的"待办"提示）。

        包括：待处理的举报数、待审核的勘误数等。
        """
        return await AnalyticsDAO.get_pending_counts()