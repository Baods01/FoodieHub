"""
模块化 Schema 导入
"""
from .common import ResponseModel, PaginationRequest, PaginationResponse, PaginationMeta, paginated_success
from .users import (
    UserCreate, UserLogin, UserUpdate, UserResponse,
    PasswordChange, PhoneUpdate, EmailUpdate,
    LoginResponse, UserStats, UserProfileResponse,
)
from .shops import ShopCreate, ShopUpdate, ShopResponse, ShopListItem, MenuItemResponse, MenuItemAddRequest, RatingCreate, RatingResponse, RatingDistribution
from .dict import (
    DictTypeCreate, DictTypeUpdate, DictTypeResponse, DictTypeWithChildrenResponse,
    DictDataCreate, DictDataUpdate, DictDataResponse,
)
from .favorites import FavoriteCreate, FavoriteReorderRequest, FavoriteBatchReorderRequest, FavoriteResponse
from .messages import (
    MessageMarkReadRequest, MessageDeleteRequest,
    MessageResponse, MessageUserResponse, UnreadCountResponse, MessageTypesResponse,
)
from .activities import ActivityResponse, ActivityListResponse
from .images import ImageUploadRequest, ImageResponse
from .governance import EditRequestCreate, EditRequestResponse, EditRequestListResponse
from .logs import LogResponse, LogListResponse
from .interaction import (
    CommentCreate, CommentResponse, CommentListResponse,
    ReplyCreate, ReplyResponse, ReplyListResponse,
    QuestionCreate, QuestionResponse, QuestionListResponse,
    AnswerCreate, AnswerResponse, AnswerListResponse,
    LikeToggleRequest, LikeToggleResponse, InteractionUserBrief,
)
from .complaints import (
    ComplaintCreateRequest, ComplaintHandleRequest,
    ComplaintResponse, ComplaintStatsResponse,
)

__all__ = [
    # Common
    'ResponseModel', 'PaginationRequest', 'PaginationResponse', 'PaginationMeta', 'paginated_success',
    # Users
    'UserCreate', 'UserLogin', 'UserUpdate', 'UserResponse',
    'PasswordChange', 'PhoneUpdate', 'EmailUpdate',
    'LoginResponse', 'UserStats', 'UserProfileResponse',
    # Shops
    'ShopCreate', 'ShopUpdate', 'ShopResponse', 'ShopListItem',
    # Dict
    'DictTypeCreate', 'DictTypeUpdate', 'DictTypeResponse', 'DictTypeWithChildrenResponse',
    'DictDataCreate', 'DictDataUpdate', 'DictDataResponse',
    # Favorites
    'FavoriteCreate', 'FavoriteReorderRequest', 'FavoriteBatchReorderRequest', 'FavoriteResponse',
    # Messages
    'MessageMarkReadRequest', 'MessageDeleteRequest',
    'MessageResponse', 'MessageUserResponse', 'UnreadCountResponse', 'MessageTypesResponse',
    # Activities
    'ActivityResponse', 'ActivityListResponse',
    # Governance
    'EditRequestCreate', 'EditRequestResponse', 'EditRequestListResponse',
    # Logs
    'LogResponse', 'LogListResponse',
    # Interaction
    'CommentCreate', 'CommentResponse', 'CommentListResponse',
    'ReplyCreate', 'ReplyResponse', 'ReplyListResponse',
    'QuestionCreate', 'QuestionResponse', 'QuestionListResponse',
    'AnswerCreate', 'AnswerResponse', 'AnswerListResponse',
    'LikeToggleRequest', 'LikeToggleResponse', 'InteractionUserBrief',
    # Images
    'ImageUploadRequest', 'ImageResponse',
    # Complaints
    'ComplaintCreateRequest', 'ComplaintHandleRequest', 'ComplaintResponse', 'ComplaintStatsResponse',
]
