"""
shop_service.py — 店铺业务逻辑

这是项目中**最复杂、最核心**的 Service 文件，涵盖：
1. 店铺 CRUD（创建/读取/更新/删除）
2. 多条件搜索（关键词 + 品类 + 区域 + 就餐方式 + 评分）
3. 店铺详情（包含标签、菜单、图片、评分分布）
4. 评分管理（创建/更新 + 重算平均分）
5. 菜单管理（增删改查）
6. ★ 店铺合并（最复杂的业务逻辑，in_transaction 事务）

与其他 Service 的交互：
  - 调用 DictRelDAO 管理店铺标签
  - 调用 ImageDAO 管理店铺和菜品图片
  - 调用 ViewHistoryDAO 记录浏览历史
  - 调用 FavoriteDAO 查询收藏状态

[教师可能问：店铺 Service 是不是太"重"了，要不要拆？]
  答：336 行对于一个核心业务模块来说是可以接受的。
  但如果按照"单一职责"原则，可以将菜单管理（MenuService）、
  评分管理（RatingService）拆成独立的 Service。
  当前没有拆分是因为它们都与店铺紧密耦合——菜单和评分没有独立的业务场景。
"""

from typing import Optional, List
from dao.shops_dao import ShopsDAO
from dao.dict_dao import DictRelDAO, DictDataDAO
from dao.image_dao import ImageDAO
from schemas.shops import ShopResponse, ShopListItem, MenuItemResponse, ImageBriefResponse


class ShopService:
    """店铺业务逻辑"""

    # =============================================================================
    # 创建店铺
    # =============================================================================

    @staticmethod
    async def create(
        name: str,
        dict_data_ids: Optional[List[int]] = None,
        menu_items: Optional[List[dict]] = None,
    ) -> ShopResponse:
        """
        创建店铺。

        ★ 执行顺序：
          1. 查重：检查同名店铺是否已存在（仅检查未软删除的）
             用 filter().first() 而非 get_or_none()，防止同名多条时抛出异常
             ★ 用 try/except 包裹：如果数据库查询异常，视为名称不存在（容错设计）
          2. 如果存在同名店铺，抛出 ValueError（Router 层捕获返回 400）
          3. ShopsDAO.create() → INSERT INTO shops
          4. 如果传了 dict_data_ids，逐个添加标签
             ★ 注意：这里是循环调用 DictRelDAO，不是批量插入
             但标签数量通常很少（<10），开销可以接受
          5. 如果传了 menu_items，逐个创建菜单项
          6. 调用 _build_response() 构建完整响应

        [教师可能问：查重时 try/except 捕获所有 Exception 是否太宽泛？]
          答：是的，更好的做法是只捕获 tortoise.exceptions.IntegrityError。
          当前捕获所有 Exception 会隐藏真正的程序错误（如网络超时）。
          但考虑到这是不频繁的写操作，且只有在查重失败时才会触发，
          这种容错设计的风险较低。
        """
        # 第 1 步：查重
        try:
            existing = await ShopsDAO.get_by_name(name)
        except Exception:
            existing = None
        if existing:
            raise ValueError("该店铺名称已存在")

        # 第 2 步：创建店铺
        shop = await ShopsDAO.create(name=name)

        # 第 3 步：打标签
        if dict_data_ids:
            for d_id in dict_data_ids:
                await DictRelDAO.add_dict_to_entity("shop", shop.id, d_id)

        # 第 4 步：初始菜单
        if menu_items:
            for item in menu_items:
                await ShopsDAO.create_menu(
                    shop.id, item["name"],
                    price=item.get("price"),
                    description=item.get("description"),
                )

        # 第 5 步：构建响应
        return await ShopService._build_response(shop.id)

    # =============================================================================
    # 获取店铺详情（核心读取操作）
    # =============================================================================

    @staticmethod
    async def get_by_id(shop_id: int, user_id: Optional[int] = None) -> Optional[ShopResponse]:
        """
        获取店铺详情。

        ★ 执行顺序（这是一个"读后写"操作——先查详情，再记浏览历史）：
          1. 查店铺：ShopsDAO.get_by_id(shop_id) → SELECT * FROM shops WHERE id=? AND is_active=1
          2. 如果店铺不存在，返回 None
          3. 递增浏览量：ShopsDAO.increment_view_count(shop_id)
             ★ 使用 F("view_count") + 1 的原子操作
          4. 如果 user_id 不为空，记录浏览历史（upsert）
             ViewHistoryDAO.upsert(user_id, shop_id)
          5. 如果 user_id 不为空，查询该用户是否收藏了此店铺、评分是多少
             用于前端显示"已收藏"和"您评过分"的状态
          6. 调用 _build_detail() 构建完整详情

        [教师可能问：递增浏览量和记录浏览历史应该在读取详情时做吗？]
          答：这是一个"读操作中夹杂写操作"的设计。
          每次用户查看店铺详情都会产生一次 UPDATE（view_count+1）
          和一次 INSERT/UPDATE（浏览历史）。
          对于高并发场景，应该将这些写操作异步化（如用消息队列）。
          但校园级应用下，这个开销是可以接受的。
        """
        shop = await ShopsDAO.get_by_id(shop_id)
        if not shop:
            return None

        # ★ 每次查看都递增浏览量（原子操作，安全）
        await ShopsDAO.increment_view_count(shop_id)

        # 记录浏览历史
        if user_id:
            from dao.view_history_dao import ViewHistoryDAO
            await ViewHistoryDAO.upsert(user_id, shop_id)

        # 查询当前用户的收藏/评分状态
        if user_id:
            from dao.favorite_dao import FavoriteDAO
            is_fav = await FavoriteDAO.is_favorited(user_id, shop_id)
            user_rating = await ShopsDAO.get_rating(user_id, shop_id)
        else:
            is_fav = False
            user_rating = None

        return await ShopService._build_detail(shop, is_fav, user_rating)

    # =============================================================================
    # 多条件搜索（最复杂的读操作）
    # =============================================================================

    @staticmethod
    async def search(
        keyword: Optional[str] = None,
        category_ids: Optional[List[int]] = None,
        district_ids: Optional[List[int]] = None,
        dining_method_ids: Optional[List[int]] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "favorite_count",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None,
    ) -> dict:
        """
        多条件搜索店铺。

        ★ 执行顺序：
          1. ShopsDAO.search() → 构建动态查询
             DAO 内部通过多个 if 分支动态拼接筛选条件：
             - keyword → name__icontains（模糊匹配，不区分大小写）
             - category_ids → DictRel 表查询店铺 ID 子集（多对多筛选）
             - district_ids → 同上
             - dining_method_ids → 同上
             - min_rating → average_rating__gte
             - sort_by/sort_order → order_by
             - page/page_size → offset/limit
          2. ShopsDAO.count() → 用相同条件统计总数
             注意 count() 和 search() 的筛选逻辑必须完全一致
             ★ 这是"先查数据再统计"模式，如果数据量大，可以优化为 SQL_CALC_FOUND_ROWS
          3. 如果传了 user_id，查该用户的收藏状态（用于前端显示红心图标）
             ★ 批量查询：一次查出所有收藏的 shop_id，而不是逐条查询
          4. 遍历搜索结果，每条记录：
             a. 查封面图：ImageDAO.get_first_by_entity("shop", s.id)
             b. 查标签：DictRelDAO.get_entity_dicts("shop", s.id)
             ★ 这里的 a 和 b 都是 N+1 风险点
          5. 组装 ShopListItem 列表返回

        [教师可能问：为啥搜索不用全文搜索引擎（如 Elasticsearch）？]
          答：当前只支持店铺名模糊搜索（name__icontains），
          数据量在 1000 家店铺以内时，MySQL 的 LIKE 查询加索引后性能足够。
          如果需要搜索"菜品名称"或"评论内容"，才需要考虑 ES。
          而且 ES 增加了部署和维护成本，对于课程设计项目来说没有必要。

        ★ N+1 性能分析：
          如果一页返回 20 家店铺，这里会产生：
          - 1 次 search 查询（JOIN 字典表）
          - 1 次 count 查询
          - 1 次收藏状态查询
          - 20 次封面图查询（★ N+1）
          - 20 次标签查询（★ N+1）
          总计约 43 次查询。改进方案：批量查封面图和标签，然后做内存映射。
        """
        # 第 1 步：执行搜索
        shops = await ShopsDAO.search(
            keyword=keyword, category_ids=category_ids,
            district_ids=district_ids, dining_method_ids=dining_method_ids,
            min_rating=min_rating,
            sort_by=sort_by, sort_order=sort_order,
            page=page, page_size=page_size,
        )

        # 第 2 步：统计总数
        total = await ShopsDAO.count(
            keyword=keyword, category_ids=category_ids,
            district_ids=district_ids, dining_method_ids=dining_method_ids,
            min_rating=min_rating,
        )

        # 第 3 步：批量查收藏状态
        fav_shop_ids = set()
        if user_id:
            from dao.favorite_dao import FavoriteDAO
            fav_shop_ids = set(await FavoriteDAO.get_shop_ids_by_user(user_id))

        # 第 4 步：逐条构建列表项
        items = []
        for s in shops:
            # ★ N+1：每条记录都查一次图片和标签
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

    # =============================================================================
    # 更新店铺（管理员）
    # =============================================================================

    @staticmethod
    async def update(shop_id: int, name: Optional[str] = None,
                     dict_data_ids: Optional[List[int]] = None,
                     is_active: Optional[bool] = None) -> Optional[ShopResponse]:
        """
        更新店铺信息（管理员功能）。

        ★ 标签替换逻辑：
          如果传了 dict_data_ids，采用"先清空再添加"策略：
          1. DictRelDAO.clear_entity_dicts("shop", shop_id) → 清除旧标签
          2. 循环 add_dict_to_entity 添加新标签
          这种策略的优点是简单（不需要比较新旧差异），
          缺点是如果清空后添加新标签的中间步骤失败了，
          店铺会变成"无标签"状态。但由于这里没有事务包裹，
          这种不一致确实可能发生。

          [改进方案] 如果要求强一致性，应该在这段逻辑外包 in_transaction()。
        """
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
        """封禁店铺。"""
        shop = await ShopsDAO.update(shop_id, is_banned=True)
        return shop is not None

    @staticmethod
    async def unban_shop(shop_id: int) -> bool:
        """解封店铺。"""
        shop = await ShopsDAO.update(shop_id, is_banned=False)
        return shop is not None

    @staticmethod
    async def delete(shop_id: int) -> bool:
        """
        软删除店铺。

        [教师可能问：删除店铺后，评论/收藏/问答等关联数据怎么办？]
          答：当前只软删除了店铺本身（is_active=False），
          关联数据没有被级联软删除。这意味着：
          - 评论表的 shop_id 仍然指向已删除的店铺
          - 收藏表的 shop_id 也仍然指向已删除的店铺
          - 在查询时，所有查询都加了 is_active=True 过滤，
            但关联数据没有被清理，长期会积累"孤儿"数据。
          改进方案见 comment_dao.py 中的 clear_by_shop 方法。
        """
        return await ShopsDAO.delete(shop_id)

    # =============================================================================
    # 菜单管理
    # =============================================================================

    @staticmethod
    async def get_menu(shop_id: int) -> List[MenuItemResponse]:
        """获取店铺菜单列表。"""
        items = await ShopsDAO.get_menu_by_shop(shop_id)
        return [MenuItemResponse.model_validate(i) for i in items]

    @staticmethod
    async def add_menu_item(shop_id: int, name: str,
                            price: Optional[float] = None,
                            description: Optional[str] = None) -> MenuItemResponse:
        """添加菜品。"""
        item = await ShopsDAO.create_menu(shop_id, name, price, description)
        return MenuItemResponse.model_validate(item)

    @staticmethod
    async def remove_menu_item(menu_id: int) -> bool:
        """删除菜品（软删除）。"""
        return await ShopsDAO.delete_menu(menu_id)

    # =============================================================================
    # 评分管理
    # =============================================================================

    @staticmethod
    async def rate(shop_id: int, user_id: int, score: int) -> dict:
        """
        评分/更新评分。

        ★ 执行顺序：
          1. ShopsDAO.create_or_update_rating()
             → 内部逻辑：
               a. Ratings.get_or_create(user_id, shop_id)
               b. 如果已存在则更新 score
               c. 自动触发 _recalc_average_rating() 重算平均分
          2. 查最新的平均分（刚被 recalc 更新过的）
          3. 查评分分布（1-5 星各有多少人）
          4. 返回

        [教师可能问：rating 表为什么没有唯一约束？]
          答：实际上有——在 models/shops.py 中定义了：
            class Meta:
                unique_together = [("user_id", "shop_id")]
          这保证了每个用户对每个店铺只能有一条评分记录。
          因此 get_or_create 能正确判断"已存在还是需要新建"。
        """
        await ShopsDAO.create_or_update_rating(user_id, shop_id, score)
        shop = await ShopsDAO.get_by_id(shop_id)
        dist = await ShopsDAO.get_rating_distribution(shop_id)
        return {"average_rating": shop.average_rating, "rating_distribution": dist}

    @staticmethod
    async def get_rating_distribution(shop_id: int) -> dict:
        """获取评分分布（1-5 星统计）。"""
        return await ShopsDAO.get_rating_distribution(shop_id)

    # =============================================================================
    # ★ 店铺合并（答辩杀手锏）
    # =============================================================================

    @staticmethod
    async def merge_shops(main_shop_id: int, duplicate_shop_ids: List[int]) -> ShopResponse:
        """
        将多个从属店铺的数据合并到主店铺，从属店铺标记为已合并并软删除。

        这是整个项目中**最复杂、最体现事务设计能力**的业务方法。
        全部操作包裹在 in_transaction() 中，保证原子性。

        详细注释见下方代码（因为这是答辩重点，需要逐行理解）。
        """
        from tortoise.transactions import in_transaction

        # ── 前置校验 ──
        main_shop = await ShopsDAO.get_by_id(main_shop_id, include_inactive=True)
        if not main_shop:
            raise ValueError("主店铺不存在")
        if not main_shop.is_active:
            raise ValueError("主店铺已被关闭，不能作为合并目标")

        # 过滤掉主店自身（防止误操作导致主店被软删除）
        duplicate_shop_ids = [did for did in duplicate_shop_ids if did != main_shop_id]
        if not duplicate_shop_ids:
            raise ValueError("没有可合并的从属店铺")

        new_aliases = main_shop.aliases or []
        total_view_add = 0

        # ── 开启事务（以下所有操作要么全部成功，要么全部回滚） ──
        async with in_transaction():
            for dup_id in duplicate_shop_ids:
                dup = await ShopsDAO.get_by_id(dup_id, include_inactive=True)
                if not dup or not dup.is_active:
                    continue

                new_aliases.append(dup.name)
                total_view_add += dup.view_count

                # 1. 迁移评分（同用户取高分）
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

                # 2. 迁移一级评论
                from models.interaction import ShopComments
                await ShopComments.filter(shop_id=dup_id, is_active=True).update(shop_id=main_shop_id)

                # 3. 迁移一级问题
                from models.interaction import ShopQuestions
                await ShopQuestions.filter(shop_id=dup_id, is_active=True).update(shop_id=main_shop_id)

                # 4. 迁移收藏（去重）
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

                # 5. 迁移图片
                from models.images import Images
                await Images.filter(entity_type="shop", entity_id=dup_id, is_active=True).update(entity_id=main_shop_id)

                # 6. 迁移菜单
                from models.shops import Menu
                await Menu.filter(shop_id=dup_id, is_active=True).update(shop_id=main_shop_id)

                # 7. 迁移字典标签（去重）
                dup_dicts = await DictRelDAO.get_entity_dicts("shop", dup_id)
                main_dict_ids = {d["dict_data_id"] for d in (await DictRelDAO.get_entity_dicts("shop", main_shop_id))}
                for dd in dup_dicts:
                    if dd["dict_data_id"] not in main_dict_ids:
                        await DictRelDAO.add_dict_to_entity("shop", main_shop_id, dd["dict_data_id"])

                # 8. 迁移活动记录
                from models.users import Activities
                await Activities.filter(target_type="shop", target_id=dup_id, is_active=True).update(target_id=main_shop_id)
                await Activities.filter(shop_id=dup_id, is_active=True).update(shop_id=main_shop_id)

                # 9. 更新别名 + 软删除从属店铺
                main_shop.aliases = list(set(new_aliases))
                dup.merged_into_id = main_shop_id
                dup.is_active = False
                await dup.save()

            # ── 事务末尾：重算主店铺的冗余计数器 ──
            main_shop.view_count += total_view_add
            await ShopsDAO.sync_comment_count(main_shop_id)
            await ShopsDAO.sync_favorite_count(main_shop_id)
            await ShopsDAO._recalc_average_rating(main_shop_id)
            await main_shop.save()

        return await ShopService._build_response(main_shop_id)

    # =============================================================================
    # 内部辅助方法
    # =============================================================================

    @staticmethod
    async def _build_response(shop_id: int) -> ShopResponse:
        """构建简单响应（不查用户收藏/评分状态）。"""
        shop = await ShopsDAO.get_by_id(shop_id)
        return await ShopService._build_detail(shop, is_fav=False, user_rating=None)

    @staticmethod
    async def _build_detail(shop, is_fav: bool, user_rating) -> ShopResponse:
        """
        构建店铺详情的完整响应。

        ★ 这个方法在 for 循环中查询了菜单图片，是 N+1 的重灾区：
          for m in menus:
            menu_img = await ImageDAO.get_first_by_entity("menu_item", m.id)
          如果菜单有 10 项，这里会额外查 10 次数据库。

        [教师可能问：如何优化这个 N+1？]
          答：可以先查出所有菜单项的 ID 列表 [m.id for m in menus]，
          然后调用 ImageDAO.get_by_entities("menu_item", ids) 一次查出所有图片，
          然后在 Python 中用 dict(menu_id → Image) 做映射，避免循环查库。
          示例代码：
            menu_ids = [m.id for m in menus]
            all_imgs = await ImageDAO.get_by_entities("menu_item", menu_ids)
            img_map = {img.entity_id: img for img in all_imgs}
            for m in menus:
              menu_img = img_map.get(m.id)
        """
        tags = await DictRelDAO.get_entity_dicts("shop", shop.id)
        menus = await ShopsDAO.get_menu_by_shop(shop.id)
        imgs = await ImageDAO.get_by_entity("shop", shop.id)
        dist = await ShopsDAO.get_rating_distribution(shop.id)

        dict_data = [
            {"id": t["dict_data_id"], "name": t["dict_data_name"], "dict_type_name": t["dict_type_name"]}
            for t in tags
        ]

        # ★ N+1 风险：为每个菜单项查一次图片
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
            images=[ImageBriefResponse(id=i.id, url=i.url, uploader_id=i.uploader_id) for i in imgs],
            is_favorited=is_fav,
            user_rating=user_rating,
            created_at=shop.created_at,
            updated_at=shop.updated_at,
        )