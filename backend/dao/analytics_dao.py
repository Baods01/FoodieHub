from typing import List, Dict, Optional
from datetime import datetime, timedelta
from tortoise.expressions import Q

from models.shops import Shops, Ratings, Comments
from models.users import Users, Activities
from models.dict import DictData, DictTypes, ShopDictRel
from models.logs import UserBehaviorLogs


class AnalyticsDAO:
    """统计分析数据访问层"""

    # ============ 平台概览统计 ============

    @classmethod
    async def get_platform_statistics(cls) -> dict:
        """获取平台统计数据"""
        shop_count = await cls.get_active_shop_count()
        user_count = await cls.get_active_user_count()
        comment_count = await cls.get_comment_count()
        
        return {
            "shop_count": shop_count,
            "user_count": user_count,
            "comment_count": comment_count,
            "timestamp": datetime.now().isoformat()
        }

    @classmethod
    async def get_active_shop_count(cls) -> int:
        """获取活跃店铺数量"""
        return await Shops.filter(is_active=True).count()

    @classmethod
    async def get_active_user_count(cls) -> int:
        """获取活跃用户数量"""
        return await Users.filter(is_active=True).count()

    @classmethod
    async def get_comment_count(cls) -> int:
        """获取评论总数"""
        return await Comments.filter(is_active=True).count()

    # ============ 店铺统计 ============

    @classmethod
    async def get_shop_count_by_status(cls) -> dict:
        """获取店铺状态分布统计"""
        active = await Shops.filter(is_active=True).count()
        inactive = await Shops.filter(is_active=False).count()
        
        return {
            "active": active,
            "inactive": inactive,
            "total": active + inactive
        }

    @classmethod
    async def get_shop_count_by_category(cls) -> List[Dict]:
        """获取店铺品类分布统计"""
        from tortoise.aggregation import Count
        
        # 获取品类字典类型
        category_type = await DictTypes.get_or_none(
            code="category",
            is_active=True
        )
        
        if not category_type:
            return []
        
        # 统计各品类的店铺数量
        return await ShopDictRel.filter(
            dict_data__dict_type=category_type,
            shop__is_active=True
        ).group_by("dict_data_id").annotate(count=Count("id")).all()

    @classmethod
    async def get_shop_count_by_area(cls) -> List[Dict]:
        """获取店铺区域分布统计"""
        from tortoise.aggregation import Count
        
        # 获取区域字典类型
        location_type = await DictTypes.get_or_none(
            code="location_type",
            is_active=True
        )
        
        if not location_type:
            return []
        
        # 统计各区域的店铺数量
        return await ShopDictRel.filter(
            dict_data__dict_type=location_type,
            shop__is_active=True
        ).group_by("dict_data_id").annotate(count=Count("id")).all()

    # ============ 用户统计 ============

    @classmethod
    async def get_user_count_by_role(cls) -> dict:
        """获取用户角色分布统计"""
        user_count = await Users.filter(is_active=True, role=0).count()
        admin_count = await Users.filter(is_active=True, role=1).count()
        
        return {
            "user": user_count,
            "admin": admin_count,
            "total": user_count + admin_count
        }

    # ============ 近7日新增趋势 ============

    @classmethod
    async def get_recent_activity_trend(
        cls,
        days: int = 7,
        activity_type: Optional[str] = None
    ) -> List[Dict]:
        """获取活动趋势数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = UserBehaviorLogs.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        if activity_type:
            query = query.filter(behavior_type=activity_type)
        
        logs = await query.order_by("created_at").all()
        
        # 按日期分组统计
        trend_data = []
        for i in range(days):
            date = end_date - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date.replace(hour=23, minute=59, second=59)
            
            count = sum(1 for log in logs if 
                       date_start <= log.created_at.replace(tzinfo=None) <= date_end)
            
            trend_data.insert(0, {
                "date": date_str,
                "count": count
            })
        
        return trend_data

    @classmethod
    async def get_recent_shops_trend(cls, days: int = 7) -> List[Dict]:
        """获取店铺新增趋势"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        shops = await Shops.filter(created_at__gte=start_date, created_at__lte=end_date).all()
        
        # 按日期分组统计
        trend_data = []
        for i in range(days):
            date = end_date - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            count = sum(1 for shop in shops if 
                       date.strftime("%Y-%m-%d") == shop.created_at.strftime("%Y-%m-%d"))
            
            trend_data.insert(0, {
                "date": date_str,
                "count": count
            })
        
        return trend_data

    @classmethod
    async def get_recent_users_trend(cls, days: int = 7) -> List[Dict]:
        """获取用户注册趋势"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        users = await Users.filter(created_at__gte=start_date, created_at__lte=end_date).all()
        
        # 按日期分组统计
        trend_data = []
        for i in range(days):
            date = end_date - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            count = sum(1 for user in users if 
                       date.strftime("%Y-%m-%d") == user.created_at.strftime("%Y-%m-%d"))
            
            trend_data.insert(0, {
                "date": date_str,
                "count": count
            })
        
        return trend_data

    @classmethod
    async def get_recent_comments_trend(cls, days: int = 7) -> List[Dict]:
        """获取评论新增趋势"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        comments = await Comments.filter(created_at__gte=start_date, created_at__lte=end_date).all()
        
        # 按日期分组统计
        trend_data = []
        for i in range(days):
            date = end_date - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            count = sum(1 for comment in comments if 
                       date.strftime("%Y-%m-%d") == comment.created_at.strftime("%Y-%m-%d"))
            
            trend_data.insert(0, {
                "date": date_str,
                "count": count
            })
        
        return trend_data

    # ============ 活跃用户统计 ============

    @classmethod
    async def get_active_users_count(cls, days: int = 7) -> int:
        """获取最近N日活跃用户数"""
        from tortoise.aggregation import Count
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 统计有行为日志的用户数量（去重）
        result = await UserBehaviorLogs.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            user_id__isnull=False
        ).annotate(user_count=Count("user_id", distinct=True)).first()
        
        return result.user_count if result else 0

    # ============ 评分统计 ============

    @classmethod
    async def get_rating_distribution(cls, shop_id: int) -> dict:
        """获取店铺评分分布"""
        from tortoise.aggregation import Count
        
        ratings = await Ratings.filter(shop_id=shop_id, is_active=True).all()
        
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in ratings:
            distribution[rating.score] += 1
        
        return {
            "total": len(ratings),
            "distribution": distribution
        }