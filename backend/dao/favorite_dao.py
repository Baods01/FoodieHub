"""
favorite_dao.py — 收藏数据访问层

对应 models/users.py：Favorites
仅操作 Favorites 表，不处理 toggle 业务逻辑（Service 层职责）。
"""

from typing import Optional, List
from models.users import Favorites
from models.shops import Shops


class FavoriteDAO:
    """收藏表 — Favorites"""

    # ==================== 查询 ====================

    @staticmethod
    async def get_by_id(favorite_id: int) -> Optional[Favorites]:
        return await Favorites.get_or_none(id=favorite_id, is_active=True)

    @staticmethod
    async def is_favorited(user_id: int, shop_id: int) -> bool:
        return await Favorites.filter(
            user_id=user_id, shop_id=shop_id, is_active=True,
        ).exists()

    @staticmethod
    async def list_by_user(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        用户收藏列表，按 sort_order → 收藏时间倒序，附店铺信息。
        返回：{"items": [...], "total": int, "page": int, "page_size": int}
        """
        qs = Favorites.filter(user_id=user_id, is_active=True)
        total = await qs.count()
        items = await qs.order_by("sort_order", "-created_at") \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .select_related("shop") \
            .all()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def count_by_user(user_id: int) -> int:
        return await Favorites.filter(user_id=user_id, is_active=True).count()

    @staticmethod
    async def count_by_shop(shop_id: int) -> int:
        return await Favorites.filter(shop_id=shop_id, is_active=True).count()

    @staticmethod
    async def get_shop_ids_by_user(user_id: int) -> List[int]:
        """获取用户收藏的所有店铺 ID 列表，用于批量判断收藏状态。"""
        return await Favorites.filter(
            user_id=user_id, is_active=True,
        ).values_list("shop_id", flat=True)

    # ==================== 写操作 ====================

    @staticmethod
    async def create(user_id: int, shop_id: int,
                     sort_order: int = 0) -> Favorites:
        """
        纯插入一条收藏记录。不处理重复/切换逻辑。
        """
        return await Favorites.create(
            user_id=user_id, shop_id=shop_id, sort_order=sort_order,
        )

    @staticmethod
    async def remove(user_id: int, shop_id: int) -> bool:
        """
        软删除某用户对某店铺的收藏（全部激活记录）。
        返回是否删除了至少一条。
        """
        count = await Favorites.filter(
            user_id=user_id, shop_id=shop_id, is_active=True,
        ).update(is_active=False)
        return count > 0

    @staticmethod
    async def update_sort_order(favorite_id: int,
                                sort_order: int) -> bool:
        fav = await Favorites.get_or_none(id=favorite_id, is_active=True)
        if not fav:
            return False
        fav.sort_order = sort_order
        await fav.save()
        return True
