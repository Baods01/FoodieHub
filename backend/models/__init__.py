"""
数据模型统一导出

按依赖顺序导入，避免循环引用。
所有模型通过字符串 FK 引用（如 "models.Users"），
因此 users / shops 的导入顺序不会产生运行时循环导入错误。
"""

# 1. 基础模型（无依赖）
from .base import BaseModel

# 2. 核心模型（无跨模块依赖）
from .dict import DictTypes, DictData, DictRel

# 3. 用户模块
from .users import Users, Activities, Favorites, Messages

# 4. 店铺模块
from .shops import Shops, Menu, Ratings

# 5. 资源模块
from .images import Images

# 6. 互动模块（评论 + 问答）
from .interaction import ShopComments, CommentReplies, ShopQuestions, QuestionAnswers, ContentLikes

# 7. 治理模块（举报 + 勘误）
from .governance import Complaints, ShopEditRequests

# 8. 日志模块
from .logs import OperationLog

__all__ = [
    'BaseModel',
    # 字典
    'DictTypes', 'DictData', 'DictRel',
    # 用户
    'Users', 'Activities', 'Favorites', 'Messages',
    # 店铺
    'Shops', 'Menu', 'Ratings',
    # 图片
    'Images',
    # 互动
    'ShopComments', 'CommentReplies', 'ShopQuestions', 'QuestionAnswers', 'ContentLikes',
    # 治理
    'Complaints', 'ShopEditRequests',
    # 日志
    'OperationLog',
]
