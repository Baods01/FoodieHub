"""
analytics_dao.py — 统计分析数据访问层

职责：
- 提供管理后台所需的聚合统计数据
- 复杂聚合使用 raw SQL（WITH RECURSIVE CTE、标量子查询等），
  展示 MySQL 数据库技术
- 不包含业务语义（不出现"品类""区域"等词汇），字典参数由上游传入
"""

from typing import Optional, List
from models.shops import Shops
from models.governance import Feedback


class AnalyticsDAO:
    """平台统计分析"""

    # ==================== raw SQL：概览 ====================

    @staticmethod
    async def get_overview() -> dict:
        """
        平台概览卡片数据。一条 SQL 完成多表计数。

        SQL：
            SELECT
                (SELECT COUNT(*) FROM shops    WHERE is_active=1 AND is_banned=0) AS total_shops,
                (SELECT COUNT(*) FROM users    WHERE is_active=1)                   AS total_users,
                (SELECT COUNT(*) FROM shop_comments WHERE is_active=1)             AS total_comments,
                (SELECT COUNT(*) FROM shop_questions WHERE is_active=1)            AS total_questions,
                (SELECT COUNT(*) FROM feedbacks WHERE type = "complaint" AND status='pending' AND is_active=1) AS pending_complaints,
                (SELECT COUNT(*) FROM feedbacks WHERE type = "edit_request" AND status='pending' AND is_active=1) AS pending_edits,
                (SELECT ROUND(AVG(average_rating), 1) FROM shops WHERE is_active=1 AND is_banned=0 AND average_rating > 0) AS avg_rating
        """
        from tortoise import Tortoise
        conn = Tortoise.get_connection("default")
        sql = """
            SELECT
                (SELECT COUNT(*) FROM shops              WHERE is_active = 1 AND is_banned = 0) AS total_shops,
                (SELECT COUNT(*) FROM users              WHERE is_active = 1)                    AS total_users,
                (SELECT COUNT(*) FROM shop_comments      WHERE is_active = 1) +
                    (SELECT COUNT(*) FROM comment_replies   WHERE is_active = 1) +
                    (SELECT COUNT(*) FROM shop_questions    WHERE is_active = 1) +
                    (SELECT COUNT(*) FROM question_answers  WHERE is_active = 1)            AS total_comments,
                (SELECT COUNT(*) FROM shop_questions     WHERE is_active = 1)                    AS total_questions,
                (SELECT COUNT(*) FROM complaints         WHERE status = 'pending' AND is_active = 1) AS pending_complaints,
                (SELECT COUNT(*) FROM feedbacks WHERE type = "edit_request" AND status = 'pending' AND is_active = 1) AS pending_edits,
                (SELECT ROUND(AVG(average_rating), 1)
                 FROM shops
                 WHERE is_active = 1 AND is_banned = 0 AND average_rating > 0)                  AS avg_rating
        """
        result = await conn.execute_query(sql)
        row = result[1][0] if result[1] else {}
        return {
            "total_shops": row.get("total_shops", 0),
            "total_users": row.get("total_users", 0),
            "total_comments": row.get("total_comments", 0),
            "total_questions": row.get("total_questions", 0),
            "pending_complaints": row.get("pending_complaints", 0),
            "pending_edits": row.get("pending_edits", 0),
            "avg_rating": row.get("avg_rating", 0.0),
        }

    # ==================== raw SQL：每日趋势（CTE） ====================

    @staticmethod
    async def get_daily_trends(days: int = 7) -> list:
        """
        近 N 天每日新增趋势。一条 SQL 完成日期序列生成 + 多表 LEFT JOIN 聚合。

        SQL（MySQL 8+ WITH RECURSIVE）：
            WITH RECURSIVE dates AS (
                SELECT CURDATE() - INTERVAL %s DAY AS dt
                UNION ALL
                SELECT dt + INTERVAL 1 DAY FROM dates WHERE dt < CURDATE()
            )
            SELECT
                dates.dt AS `date`,
                COALESCE(COUNT(DISTINCT s.id),  0) AS new_shops,
                COALESCE(COUNT(DISTINCT u.id),  0) AS new_users,
                COALESCE(COUNT(DISTINCT sc.id),  0) +
                    COALESCE(COUNT(DISTINCT cr.id),  0) +
                    COALESCE(COUNT(DISTINCT sq.id),  0) +
                    COALESCE(COUNT(DISTINCT qa.id),  0)                                   AS new_interactions,
                COALESCE(COUNT(DISTINCT sq.id), 0) AS new_questions
            FROM dates
            LEFT JOIN shops          s  ON s.is_active = 1         AND DATE(s.created_at)  = dates.dt
            LEFT JOIN users          u  ON u.is_active = 1         AND DATE(u.created_at)  = dates.dt
            LEFT JOIN shop_comments  sc ON sc.is_active = 1        AND DATE(sc.created_at) = dates.dt
            LEFT JOIN shop_questions sq ON sq.is_active = 1        AND DATE(sq.created_at) = dates.dt
            GROUP BY dates.dt
            ORDER BY dates.dt
        """
        from tortoise import Tortoise
        conn = Tortoise.get_connection("default")
        sql = """
            WITH RECURSIVE dates AS (
                SELECT CURDATE() - INTERVAL %s DAY AS dt
                UNION ALL
                SELECT dt + INTERVAL 1 DAY FROM dates WHERE dt < CURDATE()
            )
            SELECT
                dates.dt             AS `date`,
                COALESCE(COUNT(DISTINCT s.id),  0)  AS new_shops,
                COALESCE(COUNT(DISTINCT u.id),  0)  AS new_users,
                COALESCE(COUNT(DISTINCT sc.id), 0) +
                    COALESCE(COUNT(DISTINCT cr.id),  0) +
                    COALESCE(COUNT(DISTINCT sq.id),  0) +
                    COALESCE(COUNT(DISTINCT qa.id),  0)                                   AS new_interactions,
                COALESCE(COUNT(DISTINCT sq.id), 0)  AS new_questions
            FROM dates
            LEFT JOIN shops          s  ON s.is_active = 1    AND DATE(s.created_at)  = dates.dt
            LEFT JOIN users          u  ON u.is_active = 1    AND DATE(u.created_at)  = dates.dt
            LEFT JOIN shop_comments  sc ON sc.is_active = 1   AND DATE(sc.created_at) = dates.dt
            LEFT JOIN comment_replies cr ON cr.is_active = 1  AND DATE(cr.created_at) = dates.dt
            LEFT JOIN shop_questions sq ON sq.is_active = 1   AND DATE(sq.created_at) = dates.dt
            LEFT JOIN question_answers qa ON qa.is_active = 1 AND DATE(qa.created_at) = dates.dt
            GROUP BY dates.dt
            ORDER BY dates.dt
        """
        result = await conn.execute_query(sql, [days])
        rows = result[1] if result[1] else []
        return [
            {
                "date": r.get("date").strftime("%Y-%m-%d") if r.get("date") else "",
                "new_shops": r.get("new_shops", 0),
                "new_users": r.get("new_users", 0),
                "new_interactions": r.get("new_interactions", 0),
                "new_questions": r.get("new_questions", 0),
            }
            for r in rows
        ]

    # ==================== 字典参数聚合 ====================

    @staticmethod
    async def count_shops_by_dict_data(dict_data_ids: list) -> list:
        """
        统计一组字典标签下各标签关联的店铺数。

        Service 层调用示例：
            # 品类分布
            cat_ids = await DictDataDAO.get_ids_by_type_name('品类')
            AnalyticsDAO.count_shops_by_dict_data(cat_ids)

            # 区域分布
            area_ids = await DictDataDAO.get_ids_by_type_name('区域')
            AnalyticsDAO.count_shops_by_dict_data(area_ids)

        返回：[{"dict_data_id": 1, "dict_data_name": "火锅", "shop_count": 12}, ...]
        """
        if not dict_data_ids:
            return []

        from tortoise import Tortoise
        conn = Tortoise.get_connection("default")
        placeholders = ",".join("%s" for _ in dict_data_ids)
        sql = f"""
            SELECT
                dr.dict_data_id,
                dd.name          AS dict_data_name,
                COUNT(dr.entity_id) AS shop_count
            FROM dict_rels dr
            JOIN dict_data dd ON dd.id  = dr.dict_data_id
            JOIN shops s      ON s.id   = dr.entity_id AND s.is_active = 1 AND s.is_banned = 0
            WHERE dr.entity_type = 'shop'
              AND dr.is_active = 1
              AND dr.dict_data_id IN ({placeholders})
            GROUP BY dr.dict_data_id, dd.name
            ORDER BY shop_count DESC
        """
        result = await conn.execute_query(sql, dict_data_ids)
        rows = result[1] if result[1] else []
        return [
            {
                "dict_data_id": r.get("dict_data_id"),
                "dict_data_name": r.get("dict_data_name"),
                "shop_count": r.get("shop_count", 0),
            }
            for r in rows
        ]

    # ==================== ORM 简单查询 ====================

    @staticmethod
    async def get_top_rated_shops(limit: int = 10) -> list:
        """评分最高的店铺。"""
        shops = await Shops.filter(
            is_active=True, is_banned=False, average_rating__gt=0,
        ).order_by("-average_rating", "-favorite_count").limit(limit).all()
        return [
            {"id": s.id, "name": s.name, "average_rating": s.average_rating}
            for s in shops
        ]

    @staticmethod
    async def get_most_favorited_shops(limit: int = 10) -> list:
        """收藏最多的店铺。"""
        shops = await Shops.filter(
            is_active=True, is_banned=False,
        ).order_by("-favorite_count").limit(limit).all()
        return [
            {"id": s.id, "name": s.name, "favorite_count": s.favorite_count}
            for s in shops
        ]

    @staticmethod
    async def get_pending_counts() -> dict:
        """待处理工单数。"""
        pending_complaints = await Complaints.filter(
            status="pending", is_active=True,
        ).count()
        pending_edits = await ShopEditRequests.filter(
            status="pending", is_active=True,
        ).count()
        return {
            "pending_complaints": pending_complaints,
            "pending_edit_requests": pending_edits,
        }
