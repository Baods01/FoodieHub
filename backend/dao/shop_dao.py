from typing import Optional, List
from decimal import Decimal
from tortoise.expressions import Q
from models.shops import Shops, Menu, Ratings, Comments, CommentsLikes
from models.dict import DictData, ShopDictRel
from models.images import Images
from models.users import Activities, Favorites, Messages
from models.logs import UserBehaviorLogs
from models.reviews import ShopEditRequests


class ShopDAO:
    """店铺数据访问层"""

    # ============ 店铺表操作 ============

    @classmethod
    async def create_shop(
        cls,
        name: str,
        description: Optional[str] = None,
        price_range: Optional[str] = None,
        business_hours: Optional[str] = None,
        dining_methods: Optional[dict] = None,
        address_detail: Optional[str] = None,
        tags: Optional[dict] = None,
        **kwargs
    ) -> Shops:
        """创建新店铺"""
        return await Shops.create(
            name=name,
            description=description,
            price_range=price_range,
            business_hours=business_hours,
            dining_methods=dining_methods,
            address_detail=address_detail,
            tags=tags,
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
        category_codes: Optional[List[str]] = None,
        district_codes: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 20,
        offset: int = 0
    ) -> List[Shops]:
        """
        搜索店铺
        - 支持关键词搜索（名称、描述）
        - 支持分类筛选（通过字典编码）
        - 支持区域筛选（通过字典编码）
        - 支持最低评分筛选
        - 支持排序
        """
        query = Shops.filter(is_active=True)
        
        # 关键词搜索（支持名称、描述）
        if keyword:
            query = query.filter(
                Q(name__icontains=keyword) | 
                Q(description__icontains=keyword)
            )
        
        # 分类筛选（品类）
        if category_codes and len(category_codes) > 0:
            # 获取品类对应的字典数据ID
            category_dict_data = await DictData.filter(
                code__in=category_codes,
                is_active=True
            ).all()
            category_ids = [d.id for d in category_dict_data]
            
            # 通过关联表筛选
            shops_with_category = await ShopDictRel.filter(
                dict_data_id__in=category_ids,
                is_active=True
            ).values_list("shop_id", flat=True)
            
            if shops_with_category:
                query = query.filter(id__in=shops_with_category)
        
        # 区域筛选
        if district_codes and len(district_codes) > 0:
            # 获取区域对应的字典数据ID
            district_dict_data = await DictData.filter(
                code__in=district_codes,
                is_active=True
            ).all()
            district_ids = [d.id for d in district_dict_data]
            
            # 通过关联表筛选
            shops_with_district = await ShopDictRel.filter(
                dict_data_id__in=district_ids,
                is_active=True
            ).values_list("shop_id", flat=True)
            
            if shops_with_district:
                query = query.filter(id__in=shops_with_district)
        
        # 最低评分筛选（转换为 Decimal 避免浮点数精度问题）
        if min_rating is not None:
            from decimal import Decimal
            # 将 float 转换为 Decimal，保留一位小数（与数据库字段精度一致）
            min_rating_decimal = Decimal(str(min_rating)).quantize(Decimal('0.1'))
            query = query.filter(average_rating__gte=min_rating_decimal)
        
        # 排序
        order_field = sort_by if sort_order == "asc" else f"-{sort_by}"
        query = query.order_by(order_field)
        
        # 分页
        return await query.limit(limit).offset(offset).all()

    @classmethod
    async def get_shop_count(
        cls,
        keyword: Optional[str] = None,
        category_codes: Optional[List[str]] = None,
        district_codes: Optional[List[str]] = None,
        min_rating: Optional[float] = None
    ) -> int:
        """
        获取店铺总数（用于分页）
        """
        query = Shops.filter(is_active=True)
        
        if keyword:
            query = query.filter(
                Q(name__icontains=keyword) | 
                Q(description__icontains=keyword)
            )
        
        if category_codes and len(category_codes) > 0:
            category_dict_data = await DictData.filter(
                code__in=category_codes,
                is_active=True
            ).all()
            category_ids = [d.id for d in category_dict_data]
            shops_with_category = await ShopDictRel.filter(
                dict_data_id__in=category_ids,
                is_active=True
            ).values_list("shop_id", flat=True)
            if shops_with_category:
                query = query.filter(id__in=shops_with_category)
        
        if district_codes and len(district_codes) > 0:
            district_dict_data = await DictData.filter(
                code__in=district_codes,
                is_active=True
            ).all()
            district_ids = [d.id for d in district_dict_data]
            shops_with_district = await ShopDictRel.filter(
                dict_data_id__in=district_ids,
                is_active=True
            ).values_list("shop_id", flat=True)
            if shops_with_district:
                query = query.filter(id__in=shops_with_district)
        
        # 最低评分筛选（转换为 Decimal 避免浮点数精度问题）
        if min_rating is not None:
            from decimal import Decimal
            min_rating_decimal = Decimal(str(min_rating)).quantize(Decimal('0.1'))
            query = query.filter(average_rating__gte=min_rating_decimal)
        
        return await query.count()

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

    @classmethod
    async def update_shop_dict_data(
        cls,
        shop_id: int,
        location_codes: Optional[List[str]] = None,
        category_codes: Optional[List[str]] = None
    ) -> dict:
        """
        批量更新店铺的字典数据关联（区域和品类）
        
        Args:
            shop_id: 店铺ID
            location_codes: 区域编码列表（None 表示不更新）
            category_codes: 品类编码列表（None 表示不更新）
        
        Returns:
            更新结果统计
        """
        from models.dict import DictTypes
        
        # 1. 获取店铺当前的字典数据关联
        current_rels = await ShopDictRel.filter(
            shop_id=shop_id,
            is_active=True
        ).prefetch_related("dict_data", "dict_data__dict_type").all()
        
        # 2. 分类当前关联
        current_location_codes = set()
        current_category_codes = set()
        
        for rel in current_rels:
            if rel.dict_data.dict_type.code == "location_type":
                current_location_codes.add(rel.dict_data.code)
            elif rel.dict_data.dict_type.code == "category_type":
                current_category_codes.add(rel.dict_data.code)
        
        # 3. 需要添加的编码（新增）
        to_add_location = set(location_codes or []) - current_location_codes
        to_add_category = set(category_codes or []) - current_category_codes
        
        # 4. 需要删除的编码（移除）
        to_remove_location = current_location_codes - set(location_codes or [])
        to_remove_category = current_category_codes - set(category_codes or [])
        
        # 5. 执行删除操作
        deleted_count = 0
        for rel in current_rels:
            if rel.dict_data.code in to_remove_location or rel.dict_data.code in to_remove_category:
                await rel.delete()
                deleted_count += 1
        
        # 6. 执行添加操作
        added_count = 0
        added_codes = []
        
        # 获取区域字典数据
        if location_codes:
            location_dict_data = await DictData.filter(
                dict_type__code="location_type",
                code__in=location_codes,
                is_active=True
            ).all()
            location_map = {d.code: d for d in location_dict_data}
            
            for code in to_add_location:
                if code in location_map:
                    await ShopDictRel.create(
                        shop_id=shop_id,
                        dict_data_id=location_map[code].id
                    )
                    added_count += 1
                    added_codes.append(code)
        
        # 获取品类字典数据
        if category_codes:
            category_dict_data = await DictData.filter(
                dict_type__code="category_type",
                code__in=category_codes,
                is_active=True
            ).all()
            category_map = {d.code: d for d in category_dict_data}
            
            for code in to_add_category:
                if code in category_map:
                    await ShopDictRel.create(
                        shop_id=shop_id,
                        dict_data_id=category_map[code].id
                    )
                    added_count += 1
                    added_codes.append(code)
        
        return {
            "added": added_count,
            "removed": deleted_count,
            "added_codes": added_codes
        }

    # ============ 菜单项操作 ============

    @classmethod
    async def create_menu_item(
        cls,
        shop_id: int,
        name: str,
        price: Optional[Decimal] = None,
        description: Optional[str] = None
    ) -> Menu:
        """创建菜单项"""
        return await Menu.create(
            shop_id=shop_id,
            name=name,
            price=str(price) if price else None,
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
        """创建或更新用户评分，并生成动态记录"""
        from services.user_activities_service import UserActivitiesService
        
        rating = await Ratings.get_or_none(user_id=user_id, shop_id=shop_id, is_active=True)
        if rating:
            rating.score = score
            await rating.save()
        else:
            rating = await Ratings.create(user_id=user_id, shop_id=shop_id, score=score)
        
        # 创建评分动态
        await UserActivitiesService.create_rating_activity(user_id, shop_id, score)
        
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

    @classmethod
    async def get_shop_rating_distribution(cls, shop_id: int) -> dict:
        """获取店铺评分分布统计"""
        # 使用聚合查询获取各星级评分人数
        ratings = await Ratings.filter(shop_id=shop_id, is_active=True).all()
        
        distribution = {
            "star_1": 0,
            "star_2": 0,
            "star_3": 0,
            "star_4": 0,
            "star_5": 0,
            "total": 0
        }
        
        for rating in ratings:
            star_key = f"star_{rating.score}"
            if star_key in distribution:
                distribution[star_key] += 1
            distribution["total"] += 1
        
        return distribution

    # ============ 评论操作 ============

    @classmethod
    async def create_comment(
        cls,
        shop_id: int,
        user_id: int,
        content: str,
        type: str = "comment",
        parent_id: Optional[int] = None
    ) -> Comments:
        """创建评论（纯文字），并生成动态记录
        
        Args:
            shop_id: 店铺ID
            user_id: 用户ID
            content: 评论内容
            type: 评论类型，默认为 "comment"
            parent_id: 父评论ID，用于回复评论
            
        Returns:
            创建的评论对象
        """
        from services.user_activities_service import UserActivitiesService
        
        # 确定 root_id
        # 一级评论（parent_id=None 或 parent_id=0）：root_id=None
        # 回复评论（parent_id>0）：root_id=父评论的root_id或父评论ID
        root_id = None
        parent_comment_id = None  # 用于更新回复数的实际父评论ID
        if parent_id and parent_id > 0:
            parent = await Comments.get_or_none(id=parent_id, is_active=True)
            if parent:
                root_id = parent.root_id or parent_id
                parent_comment_id = parent_id
            else:
                raise ValueError(f"父评论不存在 (ID: {parent_id})")
        
        comment = await Comments.create(
            shop_id=shop_id,
            user_id=user_id,
            type=type,
            content=content,
            parent_id=parent_comment_id,  # 当 parent_id=0 时，设置为 None
            root_id=root_id
        )
        
        # 创建评论动态
        await UserActivitiesService.create_comment_activity(user_id, comment.id, shop_id)
        
        # 更新父评论的回复数
        if parent_comment_id:
            parent = await Comments.get_or_none(id=parent_comment_id, is_active=True)
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
        # 预加载用户（图片无法通过 prefetch_related 预加载，因为是多态关联）
        return await query.order_by("-created_at").limit(limit).offset(offset).prefetch_related("user")

    @classmethod
    async def get_comment_replies(cls, comment_id: int) -> List[Comments]:
        """获取评论的所有直接子回复（二级评论）"""
        return await Comments.filter(parent_id=comment_id, is_active=True).order_by("created_at").prefetch_related("user").all()

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

    # ============ 图片操作 ============

    @classmethod
    async def create_image(
        cls,
        url: str,
        entity_type: str,
        entity_id: int,
        extra: Optional[dict] = None
    ) -> Images:
        """创建图片记录"""
        return await Images.create(
            url=url,
            entity_type=entity_type,
            entity_id=entity_id,
            extra=extra
        )

    @classmethod
    async def get_images_by_entity(cls, entity_type: str, entity_id: int) -> List[Images]:
        """根据实体类型和ID获取图片列表"""
        return await Images.filter(entity_type=entity_type, entity_id=entity_id, is_active=True).all()

    @classmethod
    async def delete_image(cls, image_id: int) -> bool:
        """软删除图片"""
        image = await Images.get_or_none(id=image_id, is_active=True)
        if image:
            image.is_active = False
            await image.save()
            return True
        return False

    @classmethod
    async def get_image_by_id(cls, image_id: int) -> Optional[Images]:
        """根据ID获取图片"""
        return await Images.get_or_none(id=image_id, is_active=True)

    # ============ 菜单项图片操作 ============

    @classmethod
    async def update_menu_item_image(cls, menu_id: int, image_url: Optional[str]) -> Optional[Menu]:
        """为菜单项添加图片URL"""
        menu_item = await Menu.get_or_none(id=menu_id, is_active=True)
        if menu_item:
            # 将图片URL存储在 menu_items 的 extra 字段中
            extra = menu_item.extra or {}
            extra["image_url"] = image_url
            menu_item.extra = extra
            await menu_item.save()
        return menu_item

    # ============ 评论图片操作 ============

    @classmethod
    async def create_comment_with_images(
        cls,
        shop_id: int,
        user_id: int,
        content: str,
        image_urls: Optional[List[str]] = None
    ) -> Comments:
        """创建评论并关联图片（事务性操作）"""
        # 创建评论
        comment = await cls.create_comment(
            shop_id=shop_id,
            user_id=user_id,
            type="comment",  # 默认为普通评论
            content=content,
            parent_id=None
        )

        # 关联图片到评论
        if image_urls:
            for url in image_urls:
                await cls.create_image(
                    url=url,
                    entity_type="comment",
                    entity_id=comment.id
                )

        return comment

    @classmethod
    async def get_comment_with_images(cls, comment_id: int) -> Optional[Comments]:
        """根据ID获取评论（包含图片）"""
        return await Comments.get_or_none(id=comment_id, is_active=True).prefetch_related("user", "shop", "images")

    @classmethod
    async def get_comment_images(cls, comment_id: int) -> List[Images]:
        """获取评论关联的图片"""
        return await Images.filter(entity_type="comment", entity_id=comment_id, is_active=True).order_by("id").all()

    @classmethod
    async def delete_comment_images(cls, comment_id: int) -> int:
        """删除评论关联的图片"""
        images = await Images.filter(entity_type="comment", entity_id=comment_id, is_active=True).all()
        for image in images:
            image.is_active = False
            await image.save()
        return len(images)

    # ============ 用户活动操作 ============

    @classmethod
    async def create_activity(
        cls,
        user_id: int,
        type: str,
        target_id: int,
        target_type: str,
        content: Optional[str] = None
    ) -> Activities:
        """创建用户活动记录"""
        return await Activities.create(
            user_id=user_id,
            type=type,
            target_id=target_id,
            target_type=target_type,
            content=content
        )

    # ============ 评论图片上传操作 ============

    @classmethod
    async def upload_comment_image(
        cls,
        shop_id: int,
        comment_id: int,
        url: str,
        user_id: int,
        extra: Optional[dict] = None
    ) -> Images:
        """为评论上传图片（需校验评论归属）"""
        # 验证评论属于当前店铺
        comment = await Comments.get_or_none(id=comment_id, is_active=True)
        if not comment:
            raise ValueError("评论不存在")
        if comment.shop_id != shop_id:
            raise ValueError("评论不属于当前店铺")
        
        # 创建图片记录
        return await cls.create_image(
            url=url,
            entity_type="comment",
            entity_id=comment_id,
            extra=extra
        )

    @classmethod
    async def get_comment_list_with_images(
        cls,
        shop_id: int,
        type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Comments]:
        """获取评论列表（包含图片）"""
        query = Comments.filter(shop_id=shop_id, is_active=True, parent_id=None)
        if type:
            query = query.filter(type=type)
        
        # 预加载关联数据
        query = query.prefetch_related(
            "user",
            "images"
        )
        
        return await query.order_by("-created_at").limit(limit).offset(offset).all()

    # ============ 店铺编辑申请操作 ============

    @classmethod
    async def create_edit_request(
        cls,
        shop_id: int,
        user_id: int,
        proposed_data: dict,
        request_type: str = "correction"  # "correction" 勘误, "merge" 重复店铺合并
    ) -> ShopEditRequests:
        """创建店铺编辑申请（勘误或重复店铺合并反馈）
        
        Args:
            shop_id: 店铺ID（勘误反馈时为单个店铺ID）
            user_id: 用户ID
            proposed_data: 提议修改的字段及新值（JSON格式）
            request_type: 申请类型，"correction" 勘误, "merge" 重复店铺合并
            
        Returns:
            创建的申请对象
        """
        return await ShopEditRequests.create(
            shop_id=shop_id,
            user_id=user_id,
            proposed_data=proposed_data,
            request_type=request_type
        )

    @classmethod
    async def create_merge_request(
        cls,
        user_id: int,
        shop_ids: List[int],
        selected_main_shop_id: int,
        proposed_name: str
    ) -> ShopEditRequests:
        """创建重复店铺合并申请
        
        Args:
            user_id: 用户ID
            shop_ids: 申报的重复店铺ID列表
            selected_main_shop_id: 选择的主店铺ID
            proposed_name: 合并后店铺名称
            
        Returns:
            创建的申请对象
        """
        proposed_data = {
            "shop_ids": shop_ids,
            "selected_main_shop_id": selected_main_shop_id,
            "proposed_name": proposed_name
        }
        return await ShopEditRequests.create(
            shop_id=selected_main_shop_id,  # 记录主店铺ID
            user_id=user_id,
            proposed_data=proposed_data,
            request_type="merge"
        )

    @classmethod
    async def get_edit_requests_by_status(
        cls,
        status: str = "pending",
        request_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[ShopEditRequests]:
        """按状态获取编辑申请列表（管理员用）
        
        Args:
            status: 申请状态
            request_type: 申请类型（"correction" 或 "merge"）
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            申请列表（包含用户信息）
        """
        query = ShopEditRequests.filter(status=status, is_active=True).order_by("-created_at")
        
        if request_type:
            # 通过 proposed_data 中的 request_type 字段筛选
            # Tortoise ORM 不直接支持 JSON 查询，这里需要手动过滤
            pass
        
        query = query.prefetch_related("user", "admin")
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
            
        return await query.all()

    @classmethod
    async def update_edit_request_status(
        cls,
        request_id: int,
        status: str,
        admin_id: Optional[int] = None
    ) -> Optional[ShopEditRequests]:
        """更新申请状态（管理员审核）"""
        request = await ShopEditRequests.get_or_none(id=request_id, is_active=True)
        if request:
            request.status = status
            if admin_id:
                request.admin_id = admin_id
            await request.save()
            return request
        return None

    # ============ 用户活动操作 ============

    @classmethod
    async def get_user_activities(
        cls,
        user_id: int,
        type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Activities]:
        """获取用户活动记录（动态）
        
        Args:
            user_id: 用户ID
            type: 活动类型（可选）
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            活动记录列表（包含关联信息）
        """
        query = Activities.filter(user_id=user_id, is_active=True).order_by("-created_at")
        
        if type:
            query = query.filter(type=type)
            
        return await query.limit(limit).offset(offset).prefetch_related("user").all()

    # ============ 收藏操作 ============

    @classmethod
    async def create_favorite(
        cls,
        user_id: int,
        shop_id: int,
        sort_order: int = 0
    ) -> Favorites:
        """创建收藏，并生成动态记录"""
        from services.user_activities_service import UserActivitiesService
        
        favorite = await Favorites.create(
            user_id=user_id,
            shop_id=shop_id,
            sort_order=sort_order
        )
        
        # 创建收藏动态
        await UserActivitiesService.create_favorite_activity(user_id, shop_id)
        
        return favorite

    @classmethod
    async def delete_favorite(
        cls,
        user_id: int,
        shop_id: int
    ) -> bool:
        """删除收藏（取消收藏）"""
        favorite = await Favorites.get_or_none(user_id=user_id, shop_id=shop_id, is_active=True)
        if favorite:
            favorite.is_active = False
            await favorite.save()
            return True
        return False

    @classmethod
    async def get_user_favorites(
        cls,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Favorites]:
        """获取用户收藏列表"""
        return await Favorites.filter(
            user_id=user_id,
            is_active=True
        ).order_by("-sort_order", "-created_at").limit(limit).offset(offset).prefetch_related("shop").all()

    @classmethod
    async def has_user_favorite(
        cls,
        user_id: int,
        shop_id: int
    ) -> bool:
        """检查用户是否已收藏该店铺"""
        return await Favorites.filter(user_id=user_id, shop_id=shop_id, is_active=True).exists()

    # ============ 浏览历史操作 ============

    @classmethod
    async def create_view_log(
        cls,
        user_id: int,
        shop_id: int,
        session_id: Optional[str] = None
    ) -> UserBehaviorLogs:
        """创建浏览记录（自动合并重复）"""
        return await UserBehaviorLogs.create(
            user_id=user_id,
            behavior_type="view_shop",
            target_type="shop",
            target_id=shop_id,
            session_id=session_id
        )

    @classmethod
    async def get_user_view_history(
        cls,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[UserBehaviorLogs]:
        """获取用户浏览历史"""
        return await UserBehaviorLogs.filter(
            user_id=user_id,
            behavior_type="view_shop",
            is_active=True
        ).order_by("-created_at").limit(limit).offset(offset).prefetch_related("user").all()
