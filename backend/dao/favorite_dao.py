from typing import Optional, List

from models.users import Favorites
from models.shops import Shops


class FavoriteDAO:
    """收藏数据访问层"""

    @classmethod
    async def is_favorited(cls, user_id: int, shop_id: int) -> bool:
        """
        检查用户是否已收藏某店铺
        """
        return await Favorites.filter(
            user_id=user_id,
            shop_id=shop_id,
            is_active=True
        ).exists()

    @classmethod
    async def add_favorite(cls, user_id: int, shop_id: int) -> Favorites:
        """
        添加收藏（自动取消之前的收藏）
        - 同一用户对同一店铺只能有一条激活的收藏记录
        - 添加新收藏时，自动软删除之前的收藏
        """
        # 先取消之前的收藏
        await Favorites.filter(
            user_id=user_id,
            shop_id=shop_id,
            is_active=True
        ).update(is_active=False)
        
        # 创建新的收藏
        return await Favorites.create(
            user_id=user_id,
            shop_id=shop_id,
            sort_order=0
        )

    @classmethod
    async def remove_favorite(cls, user_id: int, shop_id: int) -> bool:
        """
        删除收藏（软删除）
        """
        favorite = await Favorites.filter(
            user_id=user_id,
            shop_id=shop_id,
            is_active=True
        ).first()
        if favorite:
            favorite.is_active = False
            await favorite.save()
            return True
        return False

    @classmethod
    async def get_user_favorites(cls, user_id: int, limit: int = 20, offset: int = 0) -> List[Favorites]:
        """
        获取用户所有收藏
        """
        return await Favorites.filter(
            user_id=user_id,
            is_active=True
        ).order_by('sort_order', '-created_at').limit(limit).offset(offset).select_related('shop').all()

    @classmethod
    async def get_user_favorites_count(cls, user_id: int) -> int:
        """
        获取用户收藏总数
        """
        return await Favorites.filter(user_id=user_id, is_active=True).count()

    @classmethod
    async def get_shop_favorite_count(cls, shop_id: int) -> int:
        """
        获取店铺收藏数
        """
        return await Favorites.filter(shop_id=shop_id, is_active=True).count()

    @classmethod
    async def get_user_favorite_shop_ids(cls, user_id: int) -> List[int]:
        """
        获取用户收藏的店铺ID列表
        """
        favorites = await Favorites.filter(
            user_id=user_id,
            is_active=True
        ).values_list('shop_id', flat=True)
        return list(favorites)

    @classmethod
    async def update_sort_order(cls, favorite_id: int, sort_order: int) -> bool:
        """
        更新收藏的排序序号
        """
        favorite = await Favorites.filter(id=favorite_id, is_active=True).first()
        if favorite:
            favorite.sort_order = sort_order
            await favorite.save()
            return True
        return False