from typing import Optional

from models.users import Favorites, Users
from models.shops import Shops

from dao.favorite_dao import FavoriteDAO
from schemas.favorites import (
    FavoriteCreate,
    FavoriteResponse,
    FavoriteActionResponse
)


class FavoriteService:
    """收藏业务逻辑服务"""

    @staticmethod
    async def toggle_favorite(user_id: int, shop_id: int) -> FavoriteActionResponse:
        """
        收藏/取消收藏店铺（切换状态）
        - 如果已收藏，则取消收藏
        - 如果未收藏，则添加收藏
        """
        # 检查用户是否存在
        user = await Users.get_or_none(id=user_id, is_active=True)
        if not user:
            return FavoriteActionResponse(
                success=False,
                message="用户不存在",
                is_favorited=False,
                favorite_count=0
            )

        # 检查店铺是否存在
        shop = await Shops.get_or_none(id=shop_id, is_active=True)
        if not shop:
            return FavoriteActionResponse(
                success=False,
                message="店铺不存在",
                is_favorited=False,
                favorite_count=0
            )

        # 检查是否已收藏
        is_favorited = await FavoriteDAO.is_favorited(user_id, shop_id)

        if is_favorited:
            # 取消收藏
            success = await FavoriteDAO.remove_favorite(user_id, shop_id)
            if success:
                favorite_count = await FavoriteDAO.get_shop_favorite_count(shop_id)
                return FavoriteActionResponse(
                    success=True,
                    message="已取消收藏",
                    is_favorited=False,
                    favorite_count=favorite_count
                )
        else:
            # 添加收藏
            await FavoriteDAO.add_favorite(user_id, shop_id)
            favorite_count = await FavoriteDAO.get_shop_favorite_count(shop_id)
            return FavoriteActionResponse(
                success=True,
                message="已收藏",
                is_favorited=True,
                favorite_count=favorite_count
            )

        return FavoriteActionResponse(
            success=False,
            message="操作失败",
            is_favorited=is_favorited,
            favorite_count=await FavoriteDAO.get_shop_favorite_count(shop_id)
        )

    @staticmethod
    async def favorite_shop(user_id: int, shop_id: int) -> FavoriteActionResponse:
        """
        收藏店铺
        """
        # 检查用户是否存在
        user = await Users.get_or_none(id=user_id, is_active=True)
        if not user:
            return FavoriteActionResponse(
                success=False,
                message="用户不存在",
                is_favorited=False,
                favorite_count=0
            )

        # 检查店铺是否存在
        shop = await Shops.get_or_none(id=shop_id, is_active=True)
        if not shop:
            return FavoriteActionResponse(
                success=False,
                message="店铺不存在",
                is_favorited=False,
                favorite_count=0
            )

        # 检查是否已收藏
        is_favorited = await FavoriteDAO.is_favorited(user_id, shop_id)
        if is_favorited:
            return FavoriteActionResponse(
                success=False,
                message="已收藏",
                is_favorited=True,
                favorite_count=await FavoriteDAO.get_shop_favorite_count(shop_id)
            )

        # 添加收藏
        await FavoriteDAO.add_favorite(user_id, shop_id)
        favorite_count = await FavoriteDAO.get_shop_favorite_count(shop_id)
        return FavoriteActionResponse(
            success=True,
            message="已收藏",
            is_favorited=True,
            favorite_count=favorite_count
        )

    @staticmethod
    async def unfavorite_shop(user_id: int, shop_id: int) -> FavoriteActionResponse:
        """
        取消收藏
        """
        # 检查用户是否存在
        user = await Users.get_or_none(id=user_id, is_active=True)
        if not user:
            return FavoriteActionResponse(
                success=False,
                message="用户不存在",
                is_favorited=False,
                favorite_count=0
            )

        # 检查店铺是否存在
        shop = await Shops.get_or_none(id=shop_id, is_active=True)
        if not shop:
            return FavoriteActionResponse(
                success=False,
                message="店铺不存在",
                is_favorited=False,
                favorite_count=0
            )

        # 检查是否已收藏
        is_favorited = await FavoriteDAO.is_favorited(user_id, shop_id)
        if not is_favorited:
            return FavoriteActionResponse(
                success=False,
                message="未收藏",
                is_favorited=False,
                favorite_count=await FavoriteDAO.get_shop_favorite_count(shop_id)
            )

        # 删除收藏
        success = await FavoriteDAO.remove_favorite(user_id, shop_id)
        favorite_count = await FavoriteDAO.get_shop_favorite_count(shop_id)
        
        if success:
            return FavoriteActionResponse(
                success=True,
                message="已取消收藏",
                is_favorited=False,
                favorite_count=favorite_count
            )
        
        return FavoriteActionResponse(
            success=False,
            message="操作失败",
            is_favorited=True,
            favorite_count=favorite_count
        )

    @staticmethod
    async def get_user_favorites(user_id: int, limit: int = 20, offset: int = 0) -> list[FavoriteResponse]:
        """
        获取用户收藏列表
        """
        favorites = await FavoriteDAO.get_user_favorites(user_id, limit, offset)
        return [FavoriteResponse.model_validate(f) for f in favorites]

    @staticmethod
    async def get_user_favorites_count(user_id: int) -> int:
        """
        获取用户收藏总数
        """
        return await FavoriteDAO.get_user_favorites_count(user_id)

    @staticmethod
    async def get_shop_favorite_count(shop_id: int) -> int:
        """
        获取店铺收藏数
        """
        return await FavoriteDAO.get_shop_favorite_count(shop_id)