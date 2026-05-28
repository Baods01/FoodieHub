from typing import Optional, List
from dao.shops_dao import ShopsDAO
from dao.dict_dao import DictRelDAO, DictDataDAO
from dao.image_dao import ImageDAO
from schemas.shops import ShopResponse, ShopListItem, MenuItemResponse, ImageBriefResponse


class ShopService:
    """店铺业务逻辑"""

    @staticmethod
    async def create(
        name: str,
        dict_data_ids: Optional[List[int]] = None,
        menu_items: Optional[List[dict]] = None,
    ) -> ShopResponse:
        shop = await ShopsDAO.create(name=name)

        # 打标签
        if dict_data_ids:
            for d_id in dict_data_ids:
                await DictRelDAO.add_dict_to_entity("shop", shop.id, d_id)

        # 初始菜单
        if menu_items:
            for item in menu_items:
                await ShopsDAO.create_menu(
                    shop.id, item["name"],
                    price=item.get("price"),
                    description=item.get("description"),
                )

        return await ShopService._build_response(shop.id)

    @staticmethod
    async def get_by_id(shop_id: int, user_id: Optional[int] = None) -> Optional[ShopResponse]:
        shop = await ShopsDAO.get_by_id(shop_id)
        if not shop:
            return None
        await ShopsDAO.increment_view_count(shop_id)
        if user_id:
            from dao.favorite_dao import FavoriteDAO
            is_fav = await FavoriteDAO.is_favorited(user_id, shop_id)
            user_rating = await ShopsDAO.get_rating(user_id, shop_id)
        else:
            is_fav = False
            user_rating = None

        return await ShopService._build_detail(shop, is_fav, user_rating)

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
        user_id: Optional[int] = None,
    ) -> dict:
        shops = await ShopsDAO.search(
            keyword=keyword, category_ids=category_ids,
            district_ids=district_ids, min_rating=min_rating,
            sort_by=sort_by, sort_order=sort_order,
            page=page, page_size=page_size,
        )
        total = await ShopsDAO.count(
            keyword=keyword, category_ids=category_ids,
            district_ids=district_ids, min_rating=min_rating,
        )

        # 用户收藏列表
        fav_shop_ids = set()
        if user_id:
            from dao.favorite_dao import FavoriteDAO
            fav_shop_ids = set(await FavoriteDAO.get_shop_ids_by_user(user_id))

        items = []
        for s in shops:
            cover = await ImageDAO.get_first_by_entity("shop", s.id)
            tags = await DictRelDAO.get_entity_dicts("shop", s.id)
            dict_data = [
                {"id": t["dict_data_id"], "name": t["dict_data_name"]}
                for t in tags
            ]
            items.append(ShopListItem(
                id=s.id, name=s.name,
                dict_data=dict_data,
                average_rating=s.average_rating,
                view_count=s.view_count,
                favorite_count=s.favorite_count,
                comment_count=s.comment_count,
                cover_image=cover.url if cover else None,
                is_favorited=s.id in fav_shop_ids,
                created_at=s.created_at,
            ))

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def update(shop_id: int, name: Optional[str] = None,
                     dict_data_ids: Optional[List[int]] = None,
                     is_active: Optional[bool] = None) -> Optional[ShopResponse]:
        update_kw = {}
        if name is not None:
            update_kw["name"] = name
        if is_active is not None:
            update_kw["is_active"] = is_active

        if update_kw:
            shop = await ShopsDAO.update(shop_id, **update_kw)
            if not shop:
                return None

        # 替换标签
        if dict_data_ids is not None:
            await DictRelDAO.clear_entity_dicts("shop", shop_id)
            for d_id in dict_data_ids:
                await DictRelDAO.add_dict_to_entity("shop", shop_id, d_id)

        return await ShopService._build_response(shop_id)

    @staticmethod
    async def ban_shop(shop_id: int) -> bool:
        shop = await ShopsDAO.update(shop_id, is_banned=True)
        return shop is not None

    @staticmethod
    async def unban_shop(shop_id: int) -> bool:
        shop = await ShopsDAO.update(shop_id, is_banned=False)
        return shop is not None

    @staticmethod
    async def delete(shop_id: int) -> bool:
        return await ShopsDAO.delete(shop_id)

    # ==================== Menu ====================

    @staticmethod
    async def get_menu(shop_id: int) -> List[MenuItemResponse]:
        items = await ShopsDAO.get_menu_by_shop(shop_id)
        return [MenuItemResponse.model_validate(i) for i in items]

    @staticmethod
    async def add_menu_item(shop_id: int, name: str,
                            price: Optional[float] = None,
                            description: Optional[str] = None) -> MenuItemResponse:
        item = await ShopsDAO.create_menu(shop_id, name, price, description)
        return MenuItemResponse.model_validate(item)

    @staticmethod
    async def remove_menu_item(menu_id: int) -> bool:
        return await ShopsDAO.delete_menu(menu_id)

    # ==================== Ratings ====================

    @staticmethod
    async def rate(shop_id: int, user_id: int, score: int) -> dict:
        await ShopsDAO.create_or_update_rating(user_id, shop_id, score)
        shop = await ShopsDAO.get_by_id(shop_id)
        dist = await ShopsDAO.get_rating_distribution(shop_id)
        return {"average_rating": shop.average_rating, "rating_distribution": dist}

    @staticmethod
    async def get_rating_distribution(shop_id: int) -> dict:
        return await ShopsDAO.get_rating_distribution(shop_id)

    # ==================== 内部辅助 ====================

    @staticmethod
    async def _build_response(shop_id: int) -> ShopResponse:
        shop = await ShopsDAO.get_by_id(shop_id)
        return await ShopService._build_detail(shop, is_fav=False, user_rating=None)

    @staticmethod
    async def _build_detail(shop, is_fav: bool, user_rating) -> ShopResponse:
        tags = await DictRelDAO.get_entity_dicts("shop", shop.id)
        menus = await ShopsDAO.get_menu_by_shop(shop.id)
        imgs = await ImageDAO.get_by_entity("shop", shop.id)
        dist = await ShopsDAO.get_rating_distribution(shop.id)

        # DictRelDAO 返回 {dict_data_id, dict_data_name}，转成 DictDataSimpleResponse 格式
        dict_data = [
            {"id": t["dict_data_id"], "name": t["dict_data_name"]}
            for t in tags
        ]

        return ShopResponse(
            id=shop.id, name=shop.name,
            dict_data=dict_data,
            view_count=shop.view_count,
            favorite_count=shop.favorite_count,
            comment_count=shop.comment_count,
            average_rating=shop.average_rating,
            rating_distribution=dist,
            aliases=shop.aliases,
            merged_into_id=shop.merged_into_id,
            is_banned=shop.is_banned,
            menu_items=[MenuItemResponse.model_validate(m) for m in menus],
            images=[ImageBriefResponse(id=i.id, url=i.url) for i in imgs],
            is_favorited=is_fav,
            user_rating=user_rating,
            created_at=shop.created_at,
            updated_at=shop.updated_at,
        )
