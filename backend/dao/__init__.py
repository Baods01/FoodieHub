# 模块化 DAO 导入
#
# TODO — 以下旧 DAO 引用了已删除的模型，暂时注释。
#         等各自改造完成后逐步取消注释。

from .dict_dao import DictTypeDAO, DictDataDAO, DictRelDAO
from .log_dao import LogDAO
from .image_dao import ImageDAO
from .like_dao import LikeDAO

# from .user_dao import UserDAO
# from .shop_dao import ShopDAO
# from .favorite_dao import FavoriteDAO
# from .message_dao import MessageDAO
# from .complaint_dao import ComplaintDAO
# from .analytics_dao import AnalyticsDAO
# from .comments_likes_dao import CommentsLikesDAO
# from .user_activities_dao import UserActivitiesDAO

__all__ = [
    "DictTypeDAO",
    "DictDataDAO",
    "DictRelDAO",
    "LogDAO",
    "ImageDAO",
    "LikeDAO",
    # "UserDAO",
    # "ShopDAO",
    # "FavoriteDAO",
    # "MessageDAO",
    # "ComplaintDAO",
    # "AnalyticsDAO",
    # "CommentsLikesDAO",
    # "UserActivitiesDAO",
]
