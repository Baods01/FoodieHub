from dao.analytics_dao import AnalyticsDAO
from dao.dict_dao import DictDataDAO


class AnalyticsService:
    """统计分析业务逻辑"""

    @staticmethod
    async def get_overview() -> dict:
        return await AnalyticsDAO.get_overview()

    @staticmethod
    async def get_daily_trends(days: int = 7) -> list:
        return await AnalyticsDAO.get_daily_trends(days)

    @staticmethod
    async def get_shop_category_distribution() -> list:
        """品类分布：取"品类"字典类型的所有数据项，统计各标签店铺数。"""
        cat_items = await DictDataDAO.get_by_type_name("品类")
        ids = [item.id for item in cat_items]
        return await AnalyticsDAO.count_shops_by_dict_data(ids)

    @staticmethod
    async def get_top_rated_shops(limit: int = 10) -> list:
        return await AnalyticsDAO.get_top_rated_shops(limit)

    @staticmethod
    async def get_most_favorited_shops(limit: int = 10) -> list:
        return await AnalyticsDAO.get_most_favorited_shops(limit)

    @staticmethod
    async def get_pending_counts() -> dict:
        return await AnalyticsDAO.get_pending_counts()
