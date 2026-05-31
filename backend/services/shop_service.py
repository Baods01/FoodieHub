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
        # 记录浏览历史
        if user_id:
            from dao.view_history_dao import ViewHistoryDAO
            await ViewHistoryDAO.upsert(user_id, shop_id)
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
                {"id": t["dict_data_id"], "name": t["dict_data_name"], "dict_type_name": t["dict_type_name"]}
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

    # ==================== 店铺合并 ====================

    @staticmethod
    async def merge_shops(main_shop_id: int, duplicate_shop_ids: List[int]) -> ShopResponse:
        """将多个从属店铺的数据合并到主店铺，从属店铺标记为已合并并软删除。"""
        from tortoise.transactions import in_transaction

        main_shop = await ShopsDAO.get_by_id(main_shop_id, include_inactive=True)
        if not main_shop:
            raise ValueError("主店铺不存在")
        if not main_shop.is_active:
            raise ValueError("主店铺已被关闭，不能作为合并目标")

        # 过滤掉主店自身（防止误操作导致主店被软删除）
        duplicate_shop_ids = [did for did in duplicate_shop_ids if did != main_shop_id]
        if not duplicate_shop_ids:
            raise ValueError("没有可合并的从属店铺")

        # 收集所有别名和浏览数
        new_aliases = main_shop.aliases or []
        total_view_add = 0

        async with in_transaction():
            for dup_id in duplicate_shop_ids:
                dup = await ShopsDAO.get_by_id(dup_id, include_inactive=True)
                if not dup or not dup.is_active:
                    continue

                new_aliases.append(dup.name)
                total_view_add += dup.view_count

                # 迁移评分（同用户取高分）
                from models.shops import Ratings
                ratings = await Ratings.filter(shop_id=dup_id, is_active=True).all()
                for r in ratings:
                    existing = await Ratings.get_or_none(shop_id=main_shop_id, user_id=r.user_id, is_active=True)
                    if existing:
                        if r.score > existing.score:
                            existing.score = r.score
                            await existing.save()
                        r.is_active = False
                        await r.save()
                    else:
                        r.shop_id = main_shop_id
                        await r.save()

                # 迁移一级评论
                from models.interaction import ShopComments
                await ShopComments.filter(shop_id=dup_id, is_active=True).update(shop_id=main_shop_id)

                # 迁移一级问题
                from models.interaction import ShopQuestions
                await ShopQuestions.filter(shop_id=dup_id, is_active=True).update(shop_id=main_shop_id)

                # 迁移收藏（去重）
                from models.users import Favorites
                dup_favs = await Favorites.filter(shop_id=dup_id, is_active=True).all()
                for f in dup_favs:
                    existed = await Favorites.get_or_none(shop_id=main_shop_id, user_id=f.user_id, is_active=True)
                    if existed:
                        f.is_active = False
                        await f.save()
                    else:
                        f.shop_id = main_shop_id
                        await f.save()

                # 迁移图片
                from models.images import Images
                await Images.filter(entity_type="shop", entity_id=dup_id, is_active=True).update(entity_id=main_shop_id)

                # 迁移菜单
                from models.shops import Menu
                await Menu.filter(shop_id=dup_id, is_active=True).update(shop_id=main_shop_id)

                # 迁移字典标签（去重）
                dup_dicts = await DictRelDAO.get_entity_dicts("shop", dup_id)
                main_dict_ids = {d["dict_data_id"] for d in (await DictRelDAO.get_entity_dicts("shop", main_shop_id))}
                for dd in dup_dicts:
                    if dd["dict_data_id"] not in main_dict_ids:
                        await DictRelDAO.add_dict_to_entity("shop", main_shop_id, dd["dict_data_id"])

                # 迁移活动记录
                from models.users import Activities
                await Activities.filter(target_type="shop", target_id=dup_id, is_active=True).update(target_id=main_shop_id)
                await Activities.filter(shop_id=dup_id, is_active=True).update(shop_id=main_shop_id)

                # 更新别名
                main_shop.aliases = list(set(new_aliases))

                # 软删除从属店铺，标记合并关系
                dup.merged_into_id = main_shop_id
                dup.is_active = False
                await dup.save()

            # 累加浏览量
            main_shop.view_count += total_view_add
            # 重算评论数和收藏数
            await ShopsDAO.sync_comment_count(main_shop_id)
            await ShopsDAO.sync_favorite_count(main_shop_id)
            # 重算平均分
            await ShopsDAO._recalc_average_rating(main_shop_id)
            await main_shop.save()

        return await ShopService._build_response(main_shop_id)

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

        # DictRelDAO 返回 {dict_data_id, dict_data_name, dict_type_name}
        dict_data = [
            {"id": t["dict_data_id"], "name": t["dict_data_name"], "dict_type_name": t["dict_type_name"]}
            for t in tags
        ]

        # 为每个菜单项查询关联图片
        menu_items = []
        for m in menus:
            menu_img = await ImageDAO.get_first_by_entity("menu_item", m.id)
            m_item = MenuItemResponse.model_validate(m)
            m_item.image = menu_img.url if menu_img else None
            menu_items.append(m_item)

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
            menu_items=menu_items,
            images=[ImageBriefResponse(id=i.id, url=i.url) for i in imgs],
            is_favorited=is_fav,
            user_rating=user_rating,
            created_at=shop.created_at,
            updated_at=shop.updated_at,
        )
