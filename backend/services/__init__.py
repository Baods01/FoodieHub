"""模块化 Service 导入"""

from .dict_service import DictService
from .log_service import LogService
from .favorite_service import FavoriteService
from .message_service import MessageService
from .complaint_service import ComplaintService
from .governance_service import GovernanceService
from .user_service import UserService
from .comment_service import CommentService
from .question_service import QuestionService
from .shop_service import ShopService
from .analytics_service import AnalyticsService
from .like_service import LikeService
from .history_service import HistoryService

__all__ = [
    "DictService",
    "LogService",
    "FavoriteService",
    "MessageService",
    "ComplaintService",
    "GovernanceService",
    "UserService",
    "CommentService",
    "QuestionService",
    "ShopService",
    "AnalyticsService",
    "LikeService",
    "HistoryService",
]
