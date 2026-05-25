# 模块化 DAO 导入
from .user_dao import UserDAO
from .shop_dao import ShopDAO
from .favorite_dao import FavoriteDAO
from .message_dao import MessageDAO
from .complaint_dao import ComplaintDAO
from .analytics_dao import AnalyticsDAO
from .comments_likes_dao import CommentsLikesDAO
from .user_activities_dao import UserActivitiesDAO

__all__ = [
    "UserDAO",
    "ShopDAO",
    "FavoriteDAO",
    "MessageDAO",
    "ComplaintDAO",
    "AnalyticsDAO",
    "CommentsLikesDAO",
    "UserActivitiesDAO",
]
