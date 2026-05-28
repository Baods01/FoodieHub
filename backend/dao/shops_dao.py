"""
shops_dao.py — 店铺模块数据访问层

对应 models/shops.py：Shops / Menu / Ratings
三张表紧密关联（菜单和评分都归属店铺），合并在一个 DAO 中。
"""

from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from tortoise.expressions import Q
from models.shops import Shops, Menu, Ratings
from models.dict import DictData, DictRel


class ShopsDAO:
    """店铺模块 — Shops + Menu + Ratings"""

    # ==================== Shops：单条查询 ====================

    @staticmethod
    async def get_by_id(shop_id: int, include_inactive: bool = False) -> Optional[Shops]:
        qs = Shops.all() if include_inactive else Shops.filter(is_active=True)
        return await qs.get_or_none(id=shop_id)

    @staticmethod
    async def get_by_name(name: str) -> Optional[Shops]:
        """精确匹配名称（含别名模糊匹配，用于查重）。"""
        return await Shops.get_or_none(name=name, is_active=True)

    # ==================== Shops：搜索列表 ====================

    @staticmethod
    async def search(
        keyword: Optional[str] = None,
        category_ids: Optional[List[int]] = None,
        district_ids: Optional[List[int]] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "favorite_count",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> List[Shops]:
        """
        多条件搜索店铺。返回 Shops 实例列表，不 JOIN 字典/图片数据。
        Service 层需要完整信息时，自行组合 DictRelDAO / ImageDAO。
        """
        qs = Shops.filter(is_active=True, is_banned=False)

        # 关键词搜索
        if keyword:
            qs = qs.filter(name__icontains=keyword)

        # 品类筛选（通过 DictRel 多态关联找 shop_id）
        if category_ids:
            shop_ids = await DictRel.filter(
                entity_type="shop", dict_data_id__in=category_ids, is_active=True
            ).values_list("entity_id", flat=True)
            if shop_ids:
                qs = qs.filter(id__in=shop_ids)
            else:
                return []  # 无匹配店铺，直接返回空

        # 区域筛选
        if district_ids:
            shop_ids = await DictRel.filter(
                entity_type="shop", dict_data_id__in=district_ids, is_active=True
            ).values_list("entity_id", flat=True)
            if shop_ids:
                qs = qs.filter(id__in=shop_ids)
            else:
                return []

        # 最低评分筛选
        if min_rating is not None:
            qs = qs.filter(average_rating__gte=min_rating)

        # 排序
        order_prefix = "-" if sort_order == "desc" else ""
        qs = qs.order_by(f"{order_prefix}{sort_by}")

        return await qs.offset((page - 1) * page_size).limit(page_size).all()

    @staticmethod
    async def count(
        keyword: Optional[str] = None,
        category_ids: Optional[List[int]] = None,
        district_ids: Optional[List[int]] = None,
        min_rating: Optional[float] = None,
    ) -> int:
        """统计搜索条件下的店铺总数。"""
        qs = Shops.filter(is_active=True, is_banned=False)

        if keyword:
            qs = qs.filter(name__icontains=keyword)

        if category_ids:
            shop_ids = await DictRel.filter(
                entity_type="shop", dict_data_id__in=category_ids, is_active=True
            ).values_list("entity_id", flat=True)
            qs = qs.filter(id__in=shop_ids) if shop_ids else qs.filter(id__in=[])

        if district_ids:
            shop_ids = await DictRel.filter(
                entity_type="shop", dict_data_id__in=district_ids, is_active=True
            ).values_list("entity_id", flat=True)
            qs = qs.filter(id__in=shop_ids) if shop_ids else qs.filter(id__in=[])

        if min_rating is not None:
            qs = qs.filter(average_rating__gte=min_rating)

        return await qs.count()

    # ==================== Shops：写操作 ====================

    @staticmethod
    async def create(name: str, **kwargs) -> Shops:
        return await Shops.create(name=name, **kwargs)

    @staticmethod
    async def update(shop_id: int, **kwargs) -> Optional[Shops]:
        shop = await Shops.get_or_none(id=shop_id, is_active=True)
        if not shop:
            return None
        for k, v in kwargs.items():
            setattr(shop, k, v)
        await shop.save()
        return shop

    @staticmethod
    async def delete(shop_id: int) -> bool:
        """软删除店铺。"""
        shop = await Shops.get_or_none(id=shop_id, is_active=True)
        if not shop:
            return False
        shop.is_active = False
        await shop.save()
        return True

    @staticmethod
    async def increment_view_count(shop_id: int) -> None:
        """浏览量 +1。"""
        from tortoise.expressions import F
        await Shops.filter(id=shop_id, is_active=True).update(view_count=F("view_count") + 1)

    # ==================== Menu ====================

    @staticmethod
    async def get_menu_by_id(menu_id: int) -> Optional[Menu]:
        return await Menu.get_or_none(id=menu_id, is_active=True)

    @staticmethod
    async def get_menu_by_shop(shop_id: int) -> List[Menu]:
        return await Menu.filter(shop_id=shop_id, is_active=True).order_by("id").all()

    @staticmethod
    async def create_menu(shop_id: int, name: str, price: Optional[float] = None,
                          description: Optional[str] = None) -> Menu:
        return await Menu.create(
            shop_id=shop_id, name=name, price=price, description=description,
        )

    @staticmethod
    async def update_menu(menu_id: int, **kwargs) -> Optional[Menu]:
        item = await Menu.get_or_none(id=menu_id, is_active=True)
        if not item:
            return None
        for k, v in kwargs.items():
            setattr(item, k, v)
        await item.save()
        return item

    @staticmethod
    async def delete_menu(menu_id: int) -> bool:
        item = await Menu.get_or_none(id=menu_id, is_active=True)
        if not item:
            return False
        item.is_active = False
        await item.save()
        return True

    # ==================== Ratings ====================

    @staticmethod
    async def get_rating(user_id: int, shop_id: int) -> Optional[Ratings]:
        return await Ratings.get_or_none(
            user_id=user_id, shop_id=shop_id, is_active=True,
        )

    @staticmethod
    async def get_ratings_by_shop(shop_id: int) -> List[Ratings]:
        return await Ratings.filter(shop_id=shop_id, is_active=True).all()

    @staticmethod
    async def create_or_update_rating(user_id: int, shop_id: int, score: int) -> Ratings:
        """
        创建或更新评分，并自动重算店铺的 average_rating。
        """
        rating, created = await Ratings.get_or_create(
            user_id=user_id, shop_id=shop_id,
            defaults={"score": score, "is_active": True},
        )
        if not created:
            rating.score = score
            if not rating.is_active:
                rating.is_active = True
            await rating.save()

        # 重算平均分
        await ShopsDAO._recalc_average_rating(shop_id)
        return rating

    @staticmethod
    async def get_rating_distribution(shop_id: int) -> dict:
        """
        评分分布统计。
        返回：{"star_1": 0, "star_2": 3, "star_3": 5, "star_4": 12, "star_5": 8, "total": 28}
        """
        ratings = await Ratings.filter(shop_id=shop_id, is_active=True).all()
        dist = {f"star_{i}": 0 for i in range(1, 6)}
        for r in ratings:
            key = f"star_{r.score}"
            if key in dist:
                dist[key] += 1
        dist["total"] = len(ratings)
        return dist

    # ==================== 内部方法 ====================

    @staticmethod
    async def _recalc_average_rating(shop_id: int) -> None:
        """重新计算并更新店铺的平均评分。"""
        result = await Ratings.filter(
            shop_id=shop_id, is_active=True,
        ).all().values_list("score", flat=True)
        if not result:
            avg = 0.0
        else:
            avg = round(sum(result) / len(result), 1)
        await Shops.filter(id=shop_id).update(average_rating=avg)
