"""
favorite_service.py — 收藏业务逻辑

收藏（Favorites）是什么？
  用户可以将感兴趣的店铺加入收藏夹，方便以后快速找到。
  收藏功能的核心操作是"切换"：已经收藏→取消收藏；未收藏→收藏。

与点赞系统的异同：
  - 点赞：LikeDAO.toggle() 在 ContentLikes 表中翻转 is_active
  - 收藏：FavoriteService.toggle() 在 Favorites 表中翻转 is_active
  两者都用了"软删除切换"模式。但收藏有"排序"（sort_order）字段支持自定义顺序。

调用链路：
  POST /favorites/toggle（Router 层）
    → FavoriteService.toggle(user_id, shop_id)
      → FavoriteDAO.is_favorited()     ← 查当前状态
      → FavoriteDAO.remove() or create()  ← 切换状态
      → FavoriteDAO.count_by_shop()    ← 查最新收藏数
      → ShopsDAO.sync_favorite_count() ← 同步冗余字段

★ 冗余字段同步策略：
  toggle 的最后一步调用了 ShopsDAO.sync_favorite_count(shop_id)，
  它的执行逻辑是：重新执行 COUNT(*) FROM favorites WHERE shop_id=? AND is_active=1，
  然后将结果 UPDATE 到 shops.favorite_count。
  这叫"兜底重算"策略，而不是"每次增减 1"。
  好处：即使前面有数据不一致（如有人漏了 is_active 过滤），同步后也会被修正。
  缺点：多一次 COUNT 查询的开销。
"""

from dao.favorite_dao import FavoriteDAO
from dao.shops_dao import ShopsDAO
from dao.image_dao import ImageDAO
from schemas.favorites import FavoriteResponse


class FavoriteService:
    """收藏业务逻辑"""

    @staticmethod
    async def toggle(user_id: int, shop_id: int) -> dict:
        """
        切换收藏状态（收藏/取消收藏）。

        ★ 执行顺序：
          1. 查当前是否已收藏：FavoriteDAO.is_favorited(user_id, shop_id)
             → 查询 Favorites 表，看是否有 user_id + shop_id + is_active=True 的记录
             这个查询是幂等的（同一个用户对同一店铺只有一条激活记录）。
          2. 如果已收藏 → 取消收藏（软删除，is_active=False）
             如果未收藏 → 新增记录（is_active=True）
             这里没有用"先查再对比差异"的逻辑，直接走两个分支。
          3. 查最新的收藏总数：count_by_shop(shop_id)
             → 给前端返回实时的收藏数
          4. 同步店铺冗余字段：sync_favorite_count(shop_id)
             → 兜底重算，保证 shops.favorite_count 与 Favorites 表的实际数量一致

        [教师可能问：第 3 步和第 4 步为什么重复查询？]
          答：
          - 第 3 步（count_by_shop）的查询结果用于返回给前端，是"展示用"的。
          - 第 4 步（sync_favorite_count）是"写回"操作，将最新计数更新到 shops 表。
          - 实际上第 3 步可以省略，直接用第 4 步更新后的值从 shops 表读取。
            当前的写法多了一次 COUNT 查询，但让代码的意图更清晰：先查前端要展示的数据，
            再更新冗余字段。可以优化为直接返回 sync_favorite_count 的结果。

        [教师可能问：如果两个用户同时收藏同一个店铺会怎样？]
          答：不会出问题。因为 sync_favorite_count 是幂等的：
          - 用户 A 收藏 → 重算 count
          - 用户 B 收藏 → 重算 count
          两次重算的结果都是 2（假设之前是 0）。虽然中间可能有短暂的不一致，
          但最终结果一定是正确的。关键原因是 COUNT 是幂等的，
          而 +1 不是——如果都用了 +1，并发下可能变成 3 而不是 2。
          （这就是为什么我们用"重算"而不是"递增"策略。）
        """
        is_fav = await FavoriteDAO.is_favorited(user_id, shop_id)
        if is_fav:
            await FavoriteDAO.remove(user_id, shop_id)
        else:
            await FavoriteDAO.create(user_id, shop_id)
        count = await FavoriteDAO.count_by_shop(shop_id)
        await ShopsDAO.sync_favorite_count(shop_id)
        return {"is_favorited": not is_fav, "favorite_count": count}

    @staticmethod
    async def list(user_id: int, page: int = 1, page_size: int = 20) -> dict:
        """
        获取用户收藏列表（分页）。

        ★ 执行顺序：
          1. 调用 FavoriteDAO.list_by_user() 获取分页的收藏数据
             DAO 内部：Favorites.filter(user_id=user_id).select_related("shop")
             因为使用了 select_related，shop 关联数据会通过 JOIN 一次性查出
          2. 遍历每条收藏记录：
             a. 通过 "shop" 关联获取店铺名称
             b. 通过 ImageDAO.get_first_by_entity("shop", shop_id) 获取封面图
                ★ N+1 风险：如果一页有 20 条收藏，会额外查 20 次图片表
          3. 手动序列化为 dict

        [教师可能问：这里手动序列化的原因是？]
          答：因为 FavoriteResponse schema 中没有 shop_name 和 shop_cover 字段，
          这两个字段来源于关联表（Shops 和 Images），不在 Favorites 模型本身。
          手动序列化可以灵活地在返回数据中包含这些"额外计算"的字段。
        """
        result = await FavoriteDAO.list_by_user(user_id, page=page, page_size=page_size)
        items = []
        for fav in result["items"]:
            # ★ getattr(fav, "shop", None) 通过 select_related 预加载的关联
            # 如果没有 select_related，fav.shop 会触发一次新的 SELECT
            shop = getattr(fav, "shop", None)
            # ★ N+1 风险：for 循环中每个元素都调用了 ImageDAO
            cover = await ImageDAO.get_first_by_entity("shop", fav.shop_id) if shop else None
            items.append({
                "id": fav.id,
                "user_id": fav.user_id,
                "shop_id": fav.shop_id,
                "shop_name": shop.name if shop else None,
                "shop_cover": cover.url if cover else None,
                "created_at": fav.created_at.isoformat(),
            })
        return {
            "items": items,
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
        }

    @staticmethod
    async def list_shop_ids(user_id: int):
        """
        获取用户收藏的所有店铺 ID 列表。
        用于在搜索/列表页快速判断"哪些店铺被当前用户收藏了"，
        避免前端逐个发请求查询收藏状态。

        调用链路：
          FavoriteDAO.get_shop_ids_by_user(user_id)
            → Favorites.filter(user_id=user_id, is_active=True).values_list("shop_id", flat=True)
            返回 List[int] 格式。
        """
        return await FavoriteDAO.get_shop_ids_by_user(user_id)