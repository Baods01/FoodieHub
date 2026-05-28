"""
模块化 Schema 导入
"""
from .common import ResponseModel, PaginationRequest, PaginationResponse, PaginationMeta, paginated_success
from .users import (
    UserCreate, UserLogin, UserUpdate, UserResponse,
    PasswordChange, PhoneUpdate, EmailUpdate,
    LoginResponse, UserStats, UserProfileResponse,
)
from .shops import ShopCreate, ShopUpdate, ShopResponse, ShopListItem
from .dict import (
    DictTypeCreate, DictTypeUpdate, DictTypeResponse, DictTypeWithChildrenResponse,
    DictDataCreate, DictDataUpdate, DictDataResponse,
)
from .favorites import FavoriteCreate, FavoriteReorderRequest, FavoriteBatchReorderRequest, FavoriteResponse
from .messages import (
    MessageMarkReadRequest, MessageDeleteRequest,
    MessageResponse, MessageUserResponse, UnreadCountResponse, MessageTypesResponse,
)
from .activities import ActivityResponse, ActivityListResponse, ActivityStats
from .images import ImageUploadRequest, ImageResponse
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
    'ActivityResponse', 'ActivityListResponse', 'ActivityStats',
    # Images
    'ImageUploadRequest', 'ImageResponse',
    # Complaints
    'ComplaintCreateRequest', 'ComplaintHandleRequest', 'ComplaintResponse', 'ComplaintStatsResponse',
]
