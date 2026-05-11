from typing import Optional, List
from decimal import Decimal

from models.shops import Shops, Menu, Ratings, Comments
from models.users import Users
from models.dict import DictData
from dao.shop_dao import ShopDAO

# 调试日志开关
DEBUG_LOG = True
from schemas.shops import (
    ShopCreate, ShopUpdate, RatingCreate, CommentCreate,
    CommentUpdate, ShopMergeRequest, MenuItemCreateRequest,
    MenuItemAddRequest,
    ShopResponse, ShopListItem, MenuItemResponse, RatingResponse,
    CommentResponse, CommentUserResponse, DictDataSimpleResponse, ImageResponse,
    RatingDistribution
)
from schemas.comments import CommentCreateRequest, CommentResponse, CommentImageResponse
from schemas.images import MenuItemWithImageRequest


class ShopService:
    """店铺业务逻辑层"""

    # ============ 店铺基本操作 ============

    @classmethod
    async def create_shop(cls, user_id: int, shop_data: ShopCreate) -> ShopResponse:
        """
        创建新店铺
        - 检查店铺名称是否已存在
        - 创建店铺记录
        - 关联字典数据（通过 code 查询）
        - 可选：创建初始菜单项
        """
        if DEBUG_LOG:
            print(f"DEBUG create_shop: user_id={user_id}, shop_data={shop_data.model_dump()}")
        
        # 检查店铺名称是否已存在
        existing_shop = await ShopDAO.find_shop_by_name(shop_data.name)
        if existing_shop:
            raise ValueError(f"店铺名称 '{shop_data.name}' 已存在")

        # 查询字典数据（通过 code）
        if DEBUG_LOG:
            print(f"DEBUG create_shop: Checking dict_data with codes: {shop_data.dict_data_codes}")
        
        dict_data_list = await DictData.filter(
            code__in=shop_data.dict_data_codes,
            is_active=True
        ).all()
        
        if DEBUG_LOG:
            print(f"DEBUG create_shop: Found dict_data_list = {dict_data_list}")
            print(f"DEBUG create_shop: Total codes: {len(shop_data.dict_data_codes)}, Found: {len(dict_data_list)}")
        
        if len(dict_data_list) != len(shop_data.dict_data_codes):
            existing_codes = [d.code for d in dict_data_list]
            missing_codes = set(shop_data.dict_data_codes) - set(existing_codes)
            if DEBUG_LOG:
                print(f"DEBUG create_shop: Missing codes: {missing_codes}")
            raise ValueError(f"以下字典数据编码不存在：{', '.join(missing_codes)}")

        # 创建店铺
        shop = await ShopDAO.create_shop(
            name=shop_data.name,
            description=shop_data.description,
            price_range=shop_data.price_range,
            business_hours=shop_data.business_hours,
            dining_methods=shop_data.dining_methods,
            address_detail=shop_data.address_detail,
            tags=shop_data.tags
        )

        # 关联字典数据
        for dict_data in dict_data_list:
            await ShopDAO.add_dict_data_to_shop(shop.id, dict_data.id)

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
        - 获取评分分布统计
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

        # 获取店铺图片
        images = await ShopDAO.get_images_by_entity("shop", shop_id)
        image_list = [ImageResponse.from_orm(img) for img in images]

        # 获取评分分布统计
        rating_distribution = await ShopDAO.get_shop_rating_distribution(shop_id)

        # 检查当前用户是否已收藏
        is_favorited = False
        if current_user_id:
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
            rating_distribution=RatingDistribution(**rating_distribution),
            aliases=shop.aliases,
            merged_into_id=shop.merged_into_id,
            price_range=shop.price_range,
            business_hours=shop.business_hours,
            dining_methods=shop.dining_methods,
            address_detail=shop.address_detail,
            tags=shop.tags,
            dict_data=[DictDataSimpleResponse.from_orm(dd) for dd in dict_data_list],
            menu_items=[MenuItemResponse.from_orm(mi) for mi in menu_items],
            images=image_list,
            is_favorited=is_favorited,
            user_rating=user_rating,
            created_at=shop.created_at,
            updated_at=shop.updated_at
        )

    @classmethod
    async def search_shops(
        cls,
        keyword: Optional[str] = None,
        category_codes: Optional[List[str]] = None,
        district_codes: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "favorite_count",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        搜索店铺列表
        返回包含数据和分页信息的字典
        """
        offset = (page - 1) * page_size
        shops = await ShopDAO.search_shops(
            keyword=keyword,
            category_codes=category_codes,
            district_codes=district_codes,
            min_rating=min_rating,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=page_size,
            offset=offset
        )

        # 获取总数用于分页
        total = await ShopDAO.get_shop_count(
            keyword=keyword,
            category_codes=category_codes,
            district_codes=district_codes,
            min_rating=min_rating
        )

        # 构建列表项
        shop_list = []
        for shop in shops:
            dict_data = await ShopDAO.get_shop_dict_data(shop.id)
            
            # 获取封面图片（取第一个店铺图片）
            images = await ShopDAO.get_images_by_entity("shop", shop.id)
            cover_image = images[0].url if images else None
            
            shop_list.append(ShopListItem(
                id=shop.id,
                name=shop.name,
                description=shop.description,
                average_rating=shop.average_rating,
                view_count=shop.view_count,
                favorite_count=shop.favorite_count,
                comment_count=shop.comment_count,
                cover_image=cover_image,
                dict_data=[DictDataSimpleResponse.from_orm(dd) for dd in dict_data],
                created_at=shop.created_at
            ))

        return {
            "data": shop_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }

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
    async def create_comment_with_images(
        cls,
        user_id: int,
        shop_id: int,
        content: str,
        image_urls: Optional[List[str]] = None
    ) -> CommentResponse:
        """创建评论（支持图文）"""
        # 检查店铺是否存在
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        # 创建评论并关联图片
        comment = await ShopDAO.create_comment_with_images(
            shop_id=shop_id,
            user_id=user_id,
            content=content,
            image_urls=image_urls
        )

        # 获取完整的评论信息（包括图片）
        comment_full = await ShopDAO.get_comment_by_id(comment.id)
        
        # 获取评论关联的图片
        images = await ShopDAO.get_comment_images(comment.id)
        
        return cls._build_comment_response_with_images(comment_full, images, user_id)

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

    @classmethod
    def _build_comment_response_with_images(
        cls,
        comment: Comments,
        images: List,
        current_user_id: Optional[int] = None
    ) -> CommentResponse:
        """构建评论响应（包含图片）"""
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
            images=[CommentImageResponse(id=img.id, url=img.url, created_at=img.created_at) for img in images],
            has_liked=has_liked,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )

    # ============ 图片上传服务 ============

    @classmethod
    async def upload_shop_image(
        cls,
        user_id: int,
        shop_id: int,
        url: str,
        extra: Optional[dict] = None
    ) -> dict:
        """上传店铺环境图片"""
        # 检查店铺是否存在且在线
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        # 创建图片记录
        image = await ShopDAO.create_image(
            url=url,
            entity_type="shop",
            entity_id=shop_id,
            extra=extra
        )

        return {"message": "图片上传成功", "image_id": image.id}

    @classmethod
    async def upload_menu_image(
        cls,
        user_id: int,
        shop_id: int,
        menu_id: int,
        url: str,
        extra: Optional[dict] = None
    ) -> dict:
        """上传菜单项图片"""
        # 检查店铺和菜单项是否存在
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        menu_item = await ShopDAO.get_menu_items(shop_id)
        menu_ids = [m.id for m in menu_item]
        if menu_id not in menu_ids:
            raise ValueError("菜单项不属于该店铺")

        # 创建图片记录
        image = await ShopDAO.create_image(
            url=url,
            entity_type="menu_item",
            entity_id=menu_id,
            extra=extra
        )

        # 更新菜单项的图片字段
        await ShopDAO.update_menu_item_image(menu_id, url)

        return {"message": "菜单图片上传成功", "image_id": image.id}

    @classmethod
    async def add_menu_item(
        cls,
        shop_id: int,
        menu_item_data: MenuItemAddRequest
    ) -> MenuItemResponse:
        """为店铺添加菜单项（独立于创建店铺时的菜单）"""
        # 检查店铺是否存在且在线
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        # 创建菜单项
        menu_item = await ShopDAO.create_menu_item(
            shop_id=shop_id,
            name=menu_item_data.name,
            price=menu_item_data.price,
            description=menu_item_data.description
        )

        return MenuItemResponse.from_orm(menu_item)

    @classmethod
    async def get_menu_items(cls, shop_id: int) -> List[MenuItemResponse]:
        """获取店铺的所有菜单项"""
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        menu_items = await ShopDAO.get_menu_items(shop_id)
        return [MenuItemResponse.from_orm(mi) for mi in menu_items]

    @classmethod
    async def get_shop_images(cls, shop_id: int) -> List[dict]:
        """获取店铺的所有图片"""
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        images = await ShopDAO.get_images_by_entity("shop", shop_id)
        return [
            {
                "id": img.id,
                "url": img.url,
                "extra": img.extra,
                "created_at": img.created_at
            }
            for img in images
        ]

    @classmethod
    async def upload_comment_image(
        cls,
        user_id: int,
        shop_id: int,
        comment_id: int,
        url: str,
        extra: Optional[dict] = None
    ) -> dict:
        """为评论上传图片（需校验评论归属）"""
        # 检查店铺是否存在
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")
        
        # 调用 DAO 方法上传评论图片（包含评论归属校验）
        image = await ShopDAO.upload_comment_image(
            shop_id=shop_id,
            comment_id=comment_id,
            url=url,
            user_id=user_id,
            extra=extra
        )
        
        return {"message": "评论图片上传成功", "image_id": image.id}

    @classmethod
    async def get_menu_item_images(cls, shop_id: int) -> List[dict]:
        """获取店铺菜单项的所有图片"""
        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        menu_items = await ShopDAO.get_menu_items(shop_id)
        menu_item_images = []

        for menu_item in menu_items:
            extra = menu_item.extra or {}
            image_url = extra.get("image_url")
            if image_url:
                menu_item_images.append({
                    "menu_id": menu_item.id,
                    "menu_name": menu_item.name,
                    "image_url": image_url
                })

        return menu_item_images
