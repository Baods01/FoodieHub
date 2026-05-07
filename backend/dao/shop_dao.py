from typing import Optional, List
from tortoise.expressions import Q
from models.shops import Shops, Menu, Ratings, Comments, CommentsLikes
from models.dict import DictData, ShopDictRel


class ShopDAO:
    """店铺数据访问层"""

    # ============ 店铺表操作 ============

    @classmethod
    async def create_shop(
        cls,
        name: str,
        description: Optional[str] = None,
        **kwargs
    ) -> Shops:
        """创建新店铺"""
        return await Shops.create(
            name=name,
            description=description,
            **kwargs
        )

    @classmethod
    async def find_shop_by_id(cls, shop_id: int) -> Optional[Shops]:
        """根据 ID 查找店铺"""
        return await Shops.get_or_none(id=shop_id, is_active=True)

    @classmethod
    async def find_shop_by_name(cls, name: str) -> Optional[Shops]:
        """按名称查找店铺（精确匹配）"""
        return await Shops.get_or_none(name=name, is_active=True)

    @classmethod
    async def search_shops(
        cls,
        keyword: Optional[str] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 20,
        offset: int = 0
    ) -> List[Shops]:
        """
        搜索店铺
        - 支持关键词搜索（名称、描述、别名）
        - 支持最低评分筛选
        - 支持排序
        """
        query = Shops.filter(is_active=True)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                Q(name__icontains=keyword) | 
                Q(description__icontains=keyword)
            )
        
        # 最低评分筛选
        if min_rating is not None:
            query = query.filter(average_rating__gte=min_rating)
        
        # 排序
        order_field = sort_by if sort_order == "asc" else f"-{sort_by}"
        query = query.order_by(order_field)
        
        # 分页
        return await query.limit(limit).offset(offset).all()

    @classmethod
    async def update_shop(cls, shop_id: int, **kwargs) -> Optional[Shops]:
        """更新店铺信息"""
        shop = await Shops.get_or_none(id=shop_id, is_active=True)
        if shop:
            for key, value in kwargs.items():
                setattr(shop, key, value)
            await shop.save()
        return shop

    @classmethod
    async def delete_shop(cls, shop_id: int) -> bool:
        """软删除店铺"""
        shop = await Shops.get_or_none(id=shop_id, is_active=True)
        if shop:
            shop.is_active = False
            await shop.save()
            return True
        return False

    @classmethod
    async def increment_view_count(cls, shop_id: int) -> None:
        """增加店铺浏览量"""
        shop = await Shops.get_or_none(id=shop_id, is_active=True)
        if shop:
            shop.view_count += 1
            await shop.save()

    # ============ 店铺-字典数据关联操作 ============

    @classmethod
    async def add_dict_data_to_shop(cls, shop_id: int, dict_data_id: int) -> ShopDictRel:
        """为店铺添加字典数据关联"""
        return await ShopDictRel.create(shop_id=shop_id, dict_data_id=dict_data_id)

    @classmethod
    async def remove_dict_data_from_shop(cls, shop_id: int, dict_data_id: int) -> bool:
        """移除店铺的字典数据关联"""
        rel = await ShopDictRel.get_or_none(shop_id=shop_id, dict_data_id=dict_data_id)
        if rel:
            await rel.delete()
            return True
        return False

    @classmethod
    async def get_shop_dict_data(cls, shop_id: int) -> List[DictData]:
        """获取店铺关联的所有字典数据"""
        relations = await ShopDictRel.filter(shop_id=shop_id, is_active=True).prefetch_related("dict_data")
        return [rel.dict_data for rel in relations]

    # ============ 菜单项操作 ============

    @classmethod
    async def create_menu_item(
        cls,
        shop_id: int,
        name: str,
        price: Optional[float] = None,
        description: Optional[str] = None
    ) -> Menu:
        """创建菜单项"""
        return await Menu.create(
            shop_id=shop_id,
            name=name,
            price=price,
            description=description
        )

    @classmethod
    async def get_menu_items(cls, shop_id: int) -> List[Menu]:
        """获取店铺的所有菜单项"""
        return await Menu.filter(shop_id=shop_id, is_active=True).order_by("id").all()

    @classmethod
    async def update_menu_item(cls, menu_id: int, **kwargs) -> Optional[Menu]:
        """更新菜单项"""
        menu_item = await Menu.get_or_none(id=menu_id, is_active=True)
        if menu_item:
            for key, value in kwargs.items():
                setattr(menu_item, key, value)
            await menu_item.save()
        return menu_item

    @classmethod
    async def delete_menu_item(cls, menu_id: int) -> bool:
        """软删除菜单项"""
        menu_item = await Menu.get_or_none(id=menu_id, is_active=True)
        if menu_item:
            menu_item.is_active = False
            await menu_item.save()
            return True
        return False

    # ============ 评分操作 ============

    @classmethod
    async def create_or_update_rating(
        cls,
        user_id: int,
        shop_id: int,
        score: int
    ) -> Ratings:
        """创建或更新用户评分"""
        rating = await Ratings.get_or_none(user_id=user_id, shop_id=shop_id, is_active=True)
        if rating:
            rating.score = score
            await rating.save()
        else:
            rating = await Ratings.create(user_id=user_id, shop_id=shop_id, score=score)
        return rating

    @classmethod
    async def get_user_rating(cls, user_id: int, shop_id: int) -> Optional[Ratings]:
        """获取用户对店铺的评分"""
        return await Ratings.get_or_none(user_id=user_id, shop_id=shop_id, is_active=True)

    @classmethod
    async def get_shop_ratings(cls, shop_id: int) -> List[Ratings]:
        """获取店铺的所有评分"""
        return await Ratings.filter(shop_id=shop_id, is_active=True).all()

    @classmethod
    async def calculate_shop_average_rating(cls, shop_id: int) -> float:
        """计算店铺平均评分"""
        ratings = await cls.get_shop_ratings(shop_id)
        if not ratings:
            return 0.0
        total_score = sum(r.score for r in ratings)
        return total_score / len(ratings)

    # ============ 评论操作 ============

    @classmethod
    async def create_comment(
        cls,
        shop_id: int,
        user_id: int,
        type: str,
        content: str,
        parent_id: Optional[int] = None
    ) -> Comments:
        """创建评论/提问"""
        # 确定 root_id
        root_id = parent_id
        if parent_id:
            parent = await Comments.get_or_none(id=parent_id)
            if parent:
                root_id = parent.root_id or parent_id
        
        comment = await Comments.create(
            shop_id=shop_id,
            user_id=user_id,
            type=type,
            content=content,
            parent_id=parent_id,
            root_id=root_id
        )
        
        # 更新父评论的回复数
        if parent_id:
            parent = await Comments.get_or_none(id=parent_id)
            if parent:
                parent.reply_count += 1
                await parent.save()
        
        # 更新店铺评论数
        shop = await Shops.get_or_none(id=shop_id)
        if shop:
            shop.comment_count += 1
            await shop.save()
            
        return comment

    @classmethod
    async def get_shop_comments(
        cls,
        shop_id: int,
        type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Comments]:
        """获取店铺的一级评论/提问"""
        query = Comments.filter(shop_id=shop_id, is_active=True, parent_id=None)
        if type:
            query = query.filter(type=type)
        return await query.order_by("-created_at").limit(limit).offset(offset).prefetch_related("user")

    @classmethod
    async def get_comment_replies(cls, comment_id: int) -> List[Comments]:
        """获取评论的所有回复"""
        return await Comments.filter(root_id=comment_id, is_active=True).order_by("created_at").prefetch_related("user").all()

    @classmethod
    async def get_comment_by_id(cls, comment_id: int) -> Optional[Comments]:
        """根据ID获取评论"""
        return await Comments.get_or_none(id=comment_id, is_active=True).prefetch_related("user", "shop")

    @classmethod
    async def update_comment(cls, comment_id: int, content: str) -> Optional[Comments]:
        """更新评论内容"""
        comment = await Comments.get_or_none(id=comment_id, is_active=True)
        if comment:
            comment.content = content
            await comment.save()
        return comment

    @classmethod
    async def delete_comment(cls, comment_id: int) -> bool:
        """软删除评论"""
        comment = await Comments.get_or_none(id=comment_id, is_active=True)
        if comment:
            comment.is_active = False
            await comment.save()
            
            # 更新店铺评论数
            if comment.shop:
                shop = await Shops.get_or_none(id=comment.shop_id)
                if shop and shop.comment_count > 0:
                    shop.comment_count -= 1
                    await shop.save()
            
            # 更新父评论回复数
            if comment.parent_id:
                parent = await Comments.get_or_none(id=comment.parent_id)
                if parent and parent.reply_count > 0:
                    parent.reply_count -= 1
                    await parent.save()
                    
            return True
        return False

    # ============ 评论点赞操作 ============

    @classmethod
    async def toggle_comment_like(cls, user_id: int, comment_id: int) -> bool:
        """点赞/取消点赞评论，返回是否点赞"""
        like = await CommentsLikes.get_or_none(user_id=user_id, comment_id=comment_id, is_active=True)
        if like:
            await like.delete()
            # 减少点赞数
            comment = await Comments.get_or_none(id=comment_id)
            if comment and comment.like_count > 0:
                comment.like_count -= 1
                await comment.save()
            return False
        else:
            await CommentsLikes.create(user_id=user_id, comment_id=comment_id)
            # 增加点赞数
            comment = await Comments.get_or_none(id=comment_id)
            if comment:
                comment.like_count += 1
                await comment.save()
            return True

    @classmethod
    async def has_user_liked_comment(cls, user_id: int, comment_id: int) -> bool:
        """检查用户是否已点赞评论"""
        return await CommentsLikes.filter(user_id=user_id, comment_id=comment_id, is_active=True).exists()