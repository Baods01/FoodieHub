"""
模块化 DAO 导入
"""

from .dict_dao import DictTypeDAO, DictDataDAO, DictRelDAO
from .log_dao import LogDAO
from .image_dao import ImageDAO
from .like_dao import LikeDAO
from .user_dao import UserDAO
from .shops_dao import ShopsDAO
from .favorite_dao import FavoriteDAO
from .message_dao import MessageDAO
from .comment_dao import CommentDAO
from .question_dao import QuestionDAO
from .activity_dao import ActivityDAO
from .feedback_dao import FeedbackDAO
from .analytics_dao import AnalyticsDAO

__all__ = [
    "DictTypeDAO",
    "DictDataDAO",
    "DictRelDAO",
    "LogDAO",
    "ImageDAO",
    "LikeDAO",
    "UserDAO",
    "ShopsDAO",
    "FavoriteDAO",
    "MessageDAO",
    "CommentDAO",
    "QuestionDAO",
    "ActivityDAO",
    "ComplaintDAO",
    "EditRequestDAO",
    "AnalyticsDAO",
]
