from typing import Optional, List
from decimal import Decimal

from models.shops import Shops, Menu, Ratings, Comments
from models.users import Users
from dao.shop_dao import ShopDAO
from schemas.shops import (
    ShopCreate, ShopUpdate, RatingCreate, CommentCreate,
    CommentUpdate, ShopMergeRequest, MenuItemCreateRequest,
    ShopResponse, ShopListItem, MenuItemResponse, RatingResponse,
    CommentResponse, CommentUserResponse, DictDataSimpleResponse, ImageResponse
)


class ShopService:
    """店铺业务逻辑层"""

    # ============ 店铺基本操作 ============

    @classmethod
    async def create_shop(cls, user_id: int, shop_data: ShopCreate) -> ShopResponse:
        """
        创建新店铺
        - 检查店铺名称是否已存在
        - 创建店铺记录
        - 关联字典数据
        - 可选：创建初始菜单项
        """
        # 检查店铺名称是否已存在
        existing_shop = await ShopDAO.find_shop_by_name(shop_data.name)
        if existing_shop:
            raise ValueError(f"店铺名称 '{shop_data.name}' 已存在")

        # 创建店铺
        shop = await ShopDAO.create_shop(
            name=shop_data.name,
            description=shop_data.description
        )

        # 关联字典数据
        if shop_data.dict_data_ids:
            for dict_data_id in shop_data.dict_data_ids:
                await ShopDAO.add_dict_data_to_shop(shop.id, dict_data_id)

        # 创建初始菜单项
        if shop_data.menu_items:
            for menu_item in shop_data.menu_items:
                await ShopDAO.create_menu_item(
                    shop_id=shop.id,
                    name=menu_item.name,
                    price=menu_item.price,
                    description=menu_item.description
                )

        # 返回完整的店铺信息
        return await cls.get_shop_detail(shop.id, user_id)

    @classmethod
    async def get_shop_detail(
        cls,
        shop_id: int,
        current_user_id: Optional[int] = None
    ) -> ShopResponse:
        """
        获取店铺详情
        - 增加浏览量
        - 获取关联的字典数据
        - 获取菜单项
        - 获取当前用户的收藏状态和评分
        """
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        # 增加浏览量
        await ShopDAO.increment_view_count(shop_id)

        # 获取字典数据
        dict_data_list = await ShopDAO.get_shop_dict_data(shop_id)

        # 获取菜单项
        menu_items = await ShopDAO.get_menu_items(shop_id)

        # 检查当前用户是否已收藏
        is_favorited = False
        if current_user_id:
            # 需要导入 FavoritesDAO 或使用直接查询
            from models.users import Favorites
            is_favorited = await Favorites.filter(
                user_id=current_user_id,
                shop_id=shop_id,
                is_active=True
            ).exists()

        # 获取当前用户的评分
        user_rating = None
        if current_user_id:
            rating = await ShopDAO.get_user_rating(current_user_id, shop_id)
            if rating:
                user_rating = RatingResponse.from_orm(rating)

        # 构建响应
        return ShopResponse(
            id=shop.id,
            name=shop.name,
            description=shop.description,
            view_count=shop.view_count,
            favorite_count=shop.favorite_count,
            comment_count=shop.comment_count,
            average_rating=shop.average_rating,
            aliases=shop.aliases,
            merged_into_id=shop.merged_into_id,
            dict_data=[DictDataSimpleResponse.from_orm(dd) for dd in dict_data_list],
            menu_items=[MenuItemResponse.from_orm(mi) for mi in menu_items],
            images=[],  # TODO: 图片功能
            is_favorited=is_favorited,
            user_rating=user_rating,
            created_at=shop.created_at,
            updated_at=shop.updated_at
        )

    @classmethod
    async def search_shops(
        cls,
        keyword: Optional[str] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> List[ShopListItem]:
        """搜索店铺列表"""
        offset = (page - 1) * page_size
        shops = await ShopDAO.search_shops(
            keyword=keyword,
            min_rating=min_rating,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=page_size,
            offset=offset
        )

        # 构建列表项
        shop_list = []
        for shop in shops:
            dict_data = await ShopDAO.get_shop_dict_data(shop.id)
            shop_list.append(ShopListItem(
                id=shop.id,
                name=shop.name,
                description=shop.description,
                average_rating=shop.average_rating,
                view_count=shop.view_count,
                favorite_count=shop.favorite_count,
                comment_count=shop.comment_count,
                cover_image=None,  # TODO: 图片功能
                dict_data=[DictDataSimpleResponse.from_orm(dd) for dd in dict_data],
                created_at=shop.created_at
            ))

        return shop_list

    @classmethod
    async def update_shop(cls, shop_id: int, update_data: ShopUpdate) -> ShopResponse:
        """管理员更新店铺信息"""
        shop = await ShopDAO.update_shop(shop_id, **update_data.model_dump(exclude_none=True))
        if not shop:
            raise ValueError("店铺不存在")
        return await cls.get_shop_detail(shop_id)

    @classmethod
    async def delete_shop(cls, shop_id: int) -> bool:
        """管理员软删除店铺"""
        return await ShopDAO.delete_shop(shop_id)

    # ============ 评分操作 ============

    @classmethod
    async def rate_shop(cls, user_id: int, shop_id: int, rating_data: RatingCreate) -> RatingResponse:
        """用户对店铺评分"""
        # 检查店铺是否存在
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        # 创建或更新评分
        rating = await ShopDAO.create_or_update_rating(
            user_id=user_id,
            shop_id=shop_id,
            score=rating_data.score
        )

        # 重新计算店铺平均评分
        average_rating = await ShopDAO.calculate_shop_average_rating(shop_id)
        await ShopDAO.update_shop(shop_id, average_rating=Decimal(str(average_rating)))

        return RatingResponse.from_orm(rating)

    # ============ 评论操作 ============

    @classmethod
    async def create_comment(
        cls,
        user_id: int,
        shop_id: int,
        comment_data: CommentCreate
    ) -> CommentResponse:
        """创建评论/提问"""
        # 检查店铺是否存在
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        # 如果是回复，检查父评论是否存在
        if comment_data.parent_id:
            parent = await ShopDAO.get_comment_by_id(comment_data.parent_id)
            if not parent:
                raise ValueError("父评论不存在")

        # 创建评论
        comment = await ShopDAO.create_comment(
            shop_id=shop_id,
            user_id=user_id,
            type=comment_data.type,
            content=comment_data.content,
            parent_id=comment_data.parent_id
        )

        # 获取完整的评论信息（包括用户信息）
        comment_full = await ShopDAO.get_comment_by_id(comment.id)
        
        return cls._build_comment_response(comment_full, user_id)

    @classmethod
    async def get_shop_comments(
        cls,
        shop_id: int,
        comment_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        current_user_id: Optional[int] = None
    ) -> List[CommentResponse]:
        """获取店铺的评论/提问列表（一级评论）"""
        offset = (page - 1) * page_size
        comments = await ShopDAO.get_shop_comments(
            shop_id=shop_id,
            type=comment_type,
            limit=page_size,
            offset=offset
        )

        return [cls._build_comment_response(c, current_user_id) for c in comments]

    @classmethod
    async def update_comment(
        cls,
        user_id: int,
        comment_id: int,
        update_data: CommentUpdate
    ) -> CommentResponse:
        """更新评论（仅作者可更新）"""
        comment = await ShopDAO.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("评论不存在")
        if comment.user_id != user_id:
            raise ValueError("无权修改他人评论")

        updated_comment = await ShopDAO.update_comment(comment_id, update_data.content)
        return cls._build_comment_response(updated_comment, user_id)

    @classmethod
    async def delete_comment(cls, user_id: int, comment_id: int, is_admin: bool = False) -> bool:
        """删除评论（作者或管理员可删除）"""
        comment = await ShopDAO.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("评论不存在")
        if not is_admin and comment.user_id != user_id:
            raise ValueError("无权删除他人评论")

        return await ShopDAO.delete_comment(comment_id)

    @classmethod
    async def toggle_comment_like(cls, user_id: int, comment_id: int) -> dict:
        """点赞/取消点赞评论"""
        comment = await ShopDAO.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("评论不存在")

        is_liked = await ShopDAO.toggle_comment_like(user_id, comment_id)
        return {"is_liked": is_liked}

    @classmethod
    def _build_comment_response(
        cls,
        comment: Comments,
        current_user_id: Optional[int] = None
    ) -> CommentResponse:
        """构建评论响应（包含嵌套回复）"""
        has_liked = False
        if current_user_id:
            # 同步检查点赞状态，这里简化处理
            pass

        return CommentResponse(
            id=comment.id,
            shop_id=comment.shop_id,
            user=CommentUserResponse.from_orm(comment.user) if comment.user else None,
            type=comment.type,
            parent_id=comment.parent_id,
            content=comment.content,
            like_count=comment.like_count,
            reply_count=comment.reply_count,
            has_liked=has_liked,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )

    # ============ 菜单项操作 ============

    @classmethod
    async def add_menu_item(
        cls,
        shop_id: int,
        menu_item: MenuItemCreateRequest
    ) -> MenuItemResponse:
        """为店铺添加菜单项"""
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        menu = await ShopDAO.create_menu_item(
            shop_id=shop_id,
            name=menu_item.name,
            price=menu_item.price,
            description=menu_item.description
        )
        return MenuItemResponse.from_orm(menu)

    @classmethod
    async def get_menu_items(cls, shop_id: int) -> List[MenuItemResponse]:
        """获取店铺的所有菜单项"""
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        menu_items = await ShopDAO.get_menu_items(shop_id)
        return [MenuItemResponse.from_orm(mi) for mi in menu_items]