# 按照依赖顺序导入模型，避免循环导入
# 1. 基础模型（无依赖）
from .base import BaseModel

# 2. 核心模型（无跨模块依赖）
from .dict import DictTypes, DictData, ShopDictRel

# 3. 用户模块（依赖 Shops，通过字符串引用）
from .users import Users, Activities, Favorites, Messages

# 4. 店铺模块（依赖 Users，通过字符串引用）
from .shops import Shops, Menu, Ratings, Comments, CommentsLikes

# 5. 其他模块（依赖 Users 和 Shops）
from .logs import UserBehaviorLogs
from .reviews import ShopEditRequests
from .images import Images

__all__ = [
    'BaseModel',
    'Users',
    'Activities',
    'Favorites',
    'Messages',
    'Shops',
    'Menu',
    'Ratings',
    'Comments',
    'CommentsLikes',
    'DictTypes',
    'DictData',
    'ShopDictRel',
    'UserBehaviorLogs',
    'ShopEditRequests',
    'Images',
]