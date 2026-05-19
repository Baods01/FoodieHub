from typing import Optional, List
from decimal import Decimal
from datetime import datetime
import asyncio

from models.shops import Shops, Menu, Ratings, Comments
from models.users import Users, Favorites, Activities
from models.images import Images
from models.dict import DictData, ShopDictRel
from models.reviews import ShopEditRequests
from dao.shop_dao import ShopDAO
from dao.message_dao import MessageDAO

# 调试日志开关
DEBUG_LOG = True
from schemas.shops import (
    ShopCreate, ShopUpdate, RatingCreate, RatingResponse,
    ShopMergeRequest, MenuItemCreateRequest,
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
        current_user_id: Optional[int] = None,
        increment_view: bool = True
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

        # 详情页浏览时才增加浏览量，避免后台更新等操作误计数
        if increment_view:
            await ShopDAO.increment_view_count(shop_id)
            if current_user_id:
                await ShopDAO.create_view_log(current_user_id, shop_id)

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
    async def get_shop_redirect_target(cls, shop_id: int) -> Optional[int]:
        shop = await ShopDAO.find_shop_by_id(shop_id, include_merged=True)
        if shop and not shop.is_active and getattr(shop, 'merged_into_id', None):
            return shop.merged_into_id
        return None

    @classmethod
    async def get_user_view_history(
        cls,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        shop_id: Optional[int] = None
    ) -> dict:
        """获取用户浏览历史"""
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取浏览历史记录
        history_items = await ShopDAO.get_user_view_history_with_shop_info(
            user_id=user_id,
            limit=page_size,
            offset=offset,
            start_time=start_time,
            end_time=end_time,
            shop_id=shop_id
        )
        
        # 统计总数
        total = await ShopDAO.count_user_view_history_with_filters(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            shop_id=shop_id
        )
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "items": history_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    @classmethod
    async def delete_user_view_history_item(
        cls,
        user_id: int,
        history_id: int
    ) -> bool:
        """删除单条浏览历史"""
        return await ShopDAO.delete_view_history_item(user_id, history_id)

    @classmethod
    async def clear_user_view_history(
        cls,
        user_id: int
    ) -> int:
        """清空用户全部浏览历史"""
        return await ShopDAO.clear_user_view_history(user_id)

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
        page_size: int = 20,
        current_user_id: Optional[int] = None
    ) -> dict:
        """
        搜索店铺列表
        返回包含数据和分页信息的字典
        
        Args:
            keyword: 搜索关键词
            category_codes: 品类筛选编码列表
            district_codes: 区域筛选编码列表
            min_rating: 最低评分筛选
            sort_by: 排序字段
            sort_order: 排序方向
            page: 页码
            page_size: 每页数量
            current_user_id: 当前用户ID（用于返回收藏状态）
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

        # 如果用户已登录，获取用户所有收藏的店铺ID
        favorited_shop_ids = set()
        if current_user_id:
            from models.users import Favorites
            favorited_shop_ids = set(await Favorites.filter(
                user_id=current_user_id,
                is_active=True
            ).values_list('shop_id', flat=True))

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
                is_favorited=shop.id in favorited_shop_ids,  # 添加收藏状态
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
        """管理员更新店铺信息（支持部分字段更新）"""
        enabled_updates = update_data.get_enabled_updates()
        location_codes = enabled_updates.pop("location_codes", None)
        category_codes = enabled_updates.pop("category_codes", None)

        if "name" in enabled_updates:
            existing_shop = await ShopDAO.find_shop_by_name(enabled_updates["name"])
            if existing_shop and existing_shop.id != shop_id:
                raise ValueError("该店铺名称已被其他店铺占用")

        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        if enabled_updates:
            shop = await ShopDAO.update_shop(shop_id, **enabled_updates)
            if not shop:
                raise ValueError("店铺不存在")

        if location_codes is not None or category_codes is not None:
            await ShopDAO.update_shop_dict_data(
                shop_id=shop_id,
                location_codes=location_codes,
                category_codes=category_codes
            )

        return await cls.get_shop_detail(shop_id, increment_view=False)

    @classmethod
    async def submit_shop_correction_request(
        cls,
        user_id: int,
        shop_id: int,
        name: Optional[str] = None,
        area_dict_data_id: Optional[int] = None,
        category_dict_data_id: Optional[int] = None,
        reason: Optional[str] = None
    ) -> ShopEditRequests:
        """提交店铺信息勘误反馈"""
        from utils.logger import debug_logger

        debug_logger.info(f"[勘误反馈] 开始处理请求 - user_id: {user_id}, shop_id: {shop_id}")
        debug_logger.info(f"[勘误反馈] 输入参数 - name: {name}, area_dict_data_id: {area_dict_data_id}, category_dict_data_id: {category_dict_data_id}, reason: {reason}")

        # 将 0 值视为 None（前端可能将未填写字段设为 0）
        if area_dict_data_id == 0:
            area_dict_data_id = None
            debug_logger.info("[勘误反馈] area_dict_data_id 为 0，已设为 None")
        if category_dict_data_id == 0:
            category_dict_data_id = None
            debug_logger.info("[勘误反馈] category_dict_data_id 为 0，已设为 None")

        try:
            shop = await ShopDAO.find_shop_by_id(shop_id)
            debug_logger.info(f"[勘误反馈] 查询店铺结果 - shop: {shop}")
            if not shop:
                debug_logger.error(f"[勘误反馈] 店铺不存在 - shop_id: {shop_id}")
                raise ValueError("店铺不存在或已下线")

            if not shop.is_active:
                debug_logger.error(f"[勘误反馈] 店铺未上线 - shop_id: {shop_id}")
                raise ValueError("只能对已上线店铺提交反馈")

            if not any([name, area_dict_data_id, category_dict_data_id]):
                debug_logger.error(f"[勘误反馈] 未提供任何修改项 - name: {name}, area: {area_dict_data_id}, category: {category_dict_data_id}")
                raise ValueError("至少提供一个修改项：name、area_dict_data_id 或 category_dict_data_id")

            changes = {}
            debug_logger.info("[勘误反馈] 开始验证修改项")

            if name is not None:
                debug_logger.info(f"[勘误反馈] 验证名称 - name: {name}")
                if not isinstance(name, str):
                    debug_logger.error(f"[勘误反馈] 名称类型无效 - name: {name}")
                    raise ValueError("店铺名称必须为字符串")
                normalized_name = name.strip()
                if normalized_name.lower() in {"string", "请输入店铺名称", "请输入名称", "请输入店铺名"}:
                    debug_logger.info(f"[勘误反馈] 名称包含占位符值，忽略该字段 - name: {name}")
                    normalized_name = ""
                if not normalized_name:
                    debug_logger.info("[勘误反馈] 名称为空或占位符，忽略该字段")
                elif normalized_name == shop.name:
                    debug_logger.info(f"[勘误反馈] 名称与当前值相同，忽略该字段 - new: {normalized_name}, current: {shop.name}")
                else:
                    existing = await ShopDAO.find_shop_by_name(normalized_name)
                    if existing and existing.id != shop_id:
                        debug_logger.error(f"[勘误反馈] 名称已被占用 - name: {normalized_name}, existing_id: {existing.id}")
                        raise ValueError("该店铺名称已被其他店铺占用")
                    changes["name"] = normalized_name
                    debug_logger.info(f"[勘误反馈] 名称验证通过 - changes: {changes}")

            if area_dict_data_id is not None:
                debug_logger.info(f"[勘误反馈] 验证区域 - area_dict_data_id: {area_dict_data_id}")
                dict_data = await DictData.filter(id=area_dict_data_id, is_active=True).prefetch_related("dict_type").get_or_none()
                debug_logger.info(f"[勘误反馈] 查询区域字典结果 - dict_data: {dict_data}")
                if not dict_data or not dict_data.dict_type or dict_data.dict_type.code != "location_type":
                    debug_logger.error(f"[勘误反馈] 区域字典项无效 - id: {area_dict_data_id}, dict_data: {dict_data}, dict_type: {dict_data.dict_type if dict_data else None}")
                    raise ValueError("指定的区域字典项无效")
                current_dict_data = await ShopDAO.get_shop_dict_data(shop_id)
                current_ids = [d.id for d in current_dict_data if d.dict_type and d.dict_type.code == "location_type"]
                debug_logger.info(f"[勘误反馈] 当前区域关联 - current_ids: {current_ids}")
                if dict_data.id in current_ids:
                    debug_logger.info(f"[勘误反馈] 区域与当前值相同，忽略该字段 - new_id: {dict_data.id}, current_ids: {current_ids}")
                else:
                    changes["area"] = {"dict_data_id": dict_data.id}
                    debug_logger.info(f"[勘误反馈] 区域验证通过 - changes: {changes}")

            if category_dict_data_id is not None:
                debug_logger.info(f"[勘误反馈] 验证品类 - category_dict_data_id: {category_dict_data_id}")
                dict_data = await DictData.filter(id=category_dict_data_id, is_active=True).prefetch_related("dict_type").get_or_none()
                debug_logger.info(f"[勘误反馈] 查询品类字典结果 - dict_data: {dict_data}")
                if not dict_data or not dict_data.dict_type or dict_data.dict_type.code != "category":
                    debug_logger.error(f"[勘误反馈] 品类字典项无效 - id: {category_dict_data_id}, dict_data: {dict_data}, dict_type: {dict_data.dict_type if dict_data else None}")
                    raise ValueError("指定的品类字典项无效")
                current_dict_data = await ShopDAO.get_shop_dict_data(shop_id)
                current_ids = [d.id for d in current_dict_data if d.dict_type and d.dict_type.code == "category"]
                debug_logger.info(f"[勘误反馈] 当前品类关联 - current_ids: {current_ids}")
                if dict_data.id in current_ids:
                    debug_logger.info(f"[勘误反馈] 品类与当前值相同，忽略该字段 - new_id: {dict_data.id}, current_ids: {current_ids}")
                else:
                    changes["category"] = {"dict_data_id": dict_data.id}
                    debug_logger.info(f"[勘误反馈] 品类验证通过 - changes: {changes}")

            if not changes:
                debug_logger.error("[勘误反馈] 未检测到实际修改项，提交失败")
                raise ValueError("至少提供一个实际修改项：name、area_dict_data_id 或 category_dict_data_id")

            debug_logger.info(f"[勘误反馈] 开始检查重复请求限制 - changes: {changes}")
            for field in changes.keys():
                recent_count = await ShopDAO.count_recent_correction_requests(shop_id, user_id, field, days=7)
                debug_logger.info(f"[勘误反馈] 字段 {field} 近期请求数: {recent_count}")
                if recent_count > 0:
                    debug_logger.error(f"[勘误反馈] 字段 {field} 7天内已提交过请求")
                    raise ValueError(f"同一用户对字段 {field} 7天内仅能提交一次反馈")

            daily_count = await ShopDAO.count_today_shop_requests(shop_id)
            debug_logger.info(f"[勘误反馈] 今日店铺总请求数: {daily_count}")
            if daily_count >= 500:
                debug_logger.error(f"[勘误反馈] 店铺今日请求数已达上限 - count: {daily_count}")
                raise ValueError("该店铺当天的反馈数量已达上限，请明天再试")

            normalized_reason = ""
            if isinstance(reason, str):
                normalized_reason = reason.strip()
                if normalized_reason.lower() in {"string", "请输入理由", "请输入原因", "请输入修改原因"}:
                    debug_logger.info(f"[勘误反馈] 原因包含占位符值，忽略该字段 - reason: {reason}")
                    normalized_reason = ""

            proposed_data = {
                "type": "correction",
                "changes": changes,
                "reason": normalized_reason
            }
            debug_logger.info(f"[勘误反馈] 准备创建请求记录 - proposed_data: {proposed_data}")

            request = await ShopDAO.create_edit_request(
                shop_id=shop_id,
                user_id=user_id,
                proposed_data=proposed_data
            )
            debug_logger.info(f"[勘误反馈] 请求记录创建成功 - request_id: {request.id}")

            return request

        except ValueError as e:
            debug_logger.error(f"[勘误反馈] 业务逻辑错误 - {str(e)}")
            raise
        except Exception as e:
            debug_logger.error(f"[勘误反馈] 未知错误 - {str(e)}", exc_info=True)
            raise

    @classmethod
    async def submit_duplicate_shop_request(
        cls,
        user_id: int,
        candidate_shop_ids: List[int],
        reason: Optional[str] = None
    ) -> ShopEditRequests:
        """提交重复店铺反馈"""
        if not candidate_shop_ids or len(candidate_shop_ids) < 2:
            raise ValueError("至少选择两个疑似重复店铺")

        candidate_shop_ids = sorted(set(candidate_shop_ids))
        if len(candidate_shop_ids) < 2:
            raise ValueError("至少选择两个不同的店铺")

        for shop_id in candidate_shop_ids:
            shop = await ShopDAO.find_shop_by_id(shop_id)
            if not shop:
                raise ValueError(f"店铺ID {shop_id} 不存在或未上线")

        exists = await ShopDAO.has_duplicate_request_in_period(user_id, candidate_shop_ids, days=30)
        if exists:
            raise ValueError("同一店铺组合30天内只能提交一次重复店铺反馈")

        proposed_data = {
            "type": "merge",
            "candidate_shop_ids": candidate_shop_ids,
            "reason": reason or ""
        }

        request = await ShopDAO.create_edit_request(
            shop_id=candidate_shop_ids[0],
            user_id=user_id,
            proposed_data=proposed_data
        )
        return request

    @classmethod
    async def list_shop_edit_requests(
        cls,
        status: Optional[str] = None,
        shop_id: Optional[int] = None,
        user_id: Optional[int] = None,
        request_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[ShopEditRequests]:
        return await ShopDAO.get_shop_edit_requests_list(
            status=status,
            shop_id=shop_id,
            user_id=user_id,
            request_type=request_type,
            limit=limit,
            offset=offset
        )

    @classmethod
    async def approve_shop_edit_request(
        cls,
        request_id: int,
        admin_id: int,
        main_shop_id: Optional[int] = None
    ) -> ShopEditRequests:
        request = await ShopDAO.get_shop_edit_request_by_id(request_id)
        if not request:
            raise ValueError("申请不存在")
        if request.status != "pending":
            raise ValueError("该申请已处理，无法重复审核")

        proposed_data = request.proposed_data or {}
        request_type = proposed_data.get("type")
        if request_type == "correction":
            await cls._apply_correction_request(request)
        elif request_type in {"duplicate", "merge"}:
            if not main_shop_id:
                raise ValueError("重复店铺反馈审批时必须指定主店铺ID")
            await cls._apply_duplicate_request(request, main_shop_id, admin_id)
        else:
            raise ValueError("无法识别的申请类型")

        updated_request = await ShopDAO.update_edit_request_status(
            request_id=request_id,
            status="approved",
            admin_id=admin_id
        )
        await cls._send_edit_request_notification(updated_request, approved=True, admin_id=admin_id)
        return updated_request

    @classmethod
    async def approve_correction_request(
        cls,
        request_id: int,
        admin_id: int,
        remark: Optional[str] = None
    ) -> ShopEditRequests:
        request = await ShopDAO.get_shop_edit_request_by_id(request_id)
        if not request:
            raise ValueError("申请不存在")
        if request.status != "pending":
            raise ValueError("该申请已处理，无法重复审核")

        proposed_data = request.proposed_data or {}
        request_type = proposed_data.get("type")
        if request_type != "correction":
            raise ValueError("该申请不是店铺勘误反馈请求")

        await cls._apply_correction_request(request)

        updated_request = await ShopDAO.update_edit_request_status(
            request_id=request_id,
            status="approved",
            admin_id=admin_id
        )
        await cls._send_edit_request_notification(updated_request, approved=True, admin_id=admin_id, reason=remark)
        return updated_request

    @classmethod
    async def reject_shop_edit_request(
        cls,
        request_id: int,
        admin_id: int,
        reason: str
    ) -> ShopEditRequests:
        request = await ShopDAO.get_shop_edit_request_by_id(request_id)
        if not request:
            raise ValueError("申请不存在")
        if request.status != "pending":
            raise ValueError("该申请已处理，无法重复审核")

        updated_request = await ShopDAO.update_edit_request_status(
            request_id=request_id,
            status="rejected",
            admin_id=admin_id
        )
        await cls._send_edit_request_notification(
            updated_request,
            approved=False,
            admin_id=admin_id,
            reason=reason
        )
        return updated_request

    @classmethod
    async def _apply_correction_request(cls, request: ShopEditRequests) -> None:
        proposed_data = request.proposed_data or {}
        changes = proposed_data.get("changes") or {}
        shop_id = request.shop_id

        shop = await ShopDAO.find_shop_by_id(shop_id)
        if not shop:
            raise ValueError("店铺不存在")

        if not changes:
            raise ValueError("没有可应用的勘误修改项")

        if "name" in changes:
            name = changes.get("name")
            if not isinstance(name, str) or not name.strip():
                raise ValueError("店铺名称无效")
            existing = await ShopDAO.find_shop_by_name(name.strip())
            if existing and existing.id != shop_id:
                raise ValueError("该店铺名称已被其他店铺占用")
            await ShopDAO.update_shop(shop_id, name=name.strip())

        if "area" in changes:
            area_change = changes.get("area") or {}
            dict_data_id = area_change.get("dict_data_id")
            if not isinstance(dict_data_id, int):
                raise ValueError("area_dict_data_id 必须为整数")
            dict_data = await DictData.filter(id=dict_data_id, is_active=True).prefetch_related("dict_type").get_or_none()
            if not dict_data or not dict_data.dict_type or dict_data.dict_type.code != "location_type":
                raise ValueError("指定的区域字典项无效")
            current_rels = await ShopDictRel.filter(
                shop_id=shop_id,
                is_active=True
            ).prefetch_related("dict_data", "dict_data__dict_type").all()
            for rel in current_rels:
                if rel.dict_data and rel.dict_data.dict_type and rel.dict_data.dict_type.code == "location_type":
                    await rel.delete()
            await ShopDAO.add_dict_data_to_shop(shop_id, dict_data.id)

        if "category" in changes:
            category_change = changes.get("category") or {}
            dict_data_id = category_change.get("dict_data_id")
            if not isinstance(dict_data_id, int):
                raise ValueError("category_dict_data_id 必须为整数")
            dict_data = await DictData.filter(id=dict_data_id, is_active=True).prefetch_related("dict_type").get_or_none()
            if not dict_data or not dict_data.dict_type or dict_data.dict_type.code != "category":
                raise ValueError("指定的品类字典项无效")
            current_rels = await ShopDictRel.filter(
                shop_id=shop_id,
                is_active=True
            ).prefetch_related("dict_data", "dict_data__dict_type").all()
            for rel in current_rels:
                if rel.dict_data and rel.dict_data.dict_type and rel.dict_data.dict_type.code == "category":
                    await rel.delete()
            await ShopDAO.add_dict_data_to_shop(shop_id, dict_data.id)

    @classmethod
    async def _apply_duplicate_request(cls, request: ShopEditRequests, main_shop_id: int, admin_id: int) -> None:
        proposed_data = request.proposed_data or {}
        candidate_shop_ids = sorted(set(proposed_data.get("candidate_shop_ids") or []))
        duplicate_shop_ids = set(candidate_shop_ids)
        duplicate_shop_ids.add(request.shop_id)

        if main_shop_id not in duplicate_shop_ids:
            raise ValueError("主店铺必须是重复候选店铺之一")

        main_shop = await ShopDAO.find_shop_by_id(main_shop_id)
        if not main_shop:
            raise ValueError("主店铺不存在或已下线")

        duplicate_shop_ids.discard(main_shop_id)
        duplicate_shop_ids = list(duplicate_shop_ids)
        view_count_add = 0
        for duplicate_id in duplicate_shop_ids:
            duplicate_shop = await Shops.get_or_none(id=duplicate_id, is_active=True)
            if not duplicate_shop:
                raise ValueError(f"候选店铺 {duplicate_id} 不存在或已下线")

            view_count_add += duplicate_shop.view_count

            # 迁移评分
            ratings = await Ratings.filter(shop_id=duplicate_id, is_active=True).all()
            for rating in ratings:
                existing_rating = await Ratings.get_or_none(
                    shop_id=main_shop_id,
                    user_id=rating.user_id,
                    is_active=True
                )
                if existing_rating:
                    if rating.score > existing_rating.score:
                        existing_rating.score = rating.score
                        await existing_rating.save()
                    rating.is_active = False
                    await rating.save()
                else:
                    rating.shop_id = main_shop_id
                    await rating.save()

            # 迁移评论与问答
            await Comments.filter(shop_id=duplicate_id, is_active=True).update(shop_id=main_shop_id)

            # 迁移收藏
            duplicate_favorites = await Favorites.filter(shop_id=duplicate_id, is_active=True).all()
            for favorite in duplicate_favorites:
                existed = await Favorites.get_or_none(
                    shop_id=main_shop_id,
                    user_id=favorite.user_id,
                    is_active=True
                )
                if existed:
                    favorite.is_active = False
                    await favorite.save()
                else:
                    favorite.shop_id = main_shop_id
                    await favorite.save()

            # 迁移图片
            await Images.filter(entity_type="shop", entity_id=duplicate_id, is_active=True).update(entity_id=main_shop_id)

            # 迁移菜单
            await Menu.filter(shop_id=duplicate_id, is_active=True).update(shop_id=main_shop_id)

            # 迁移活动
            await Activities.filter(target_type="shop", target_id=duplicate_id, is_active=True).update(target_id=main_shop_id)

            # 合并字典关联
            duplicate_rels = await ShopDictRel.filter(shop_id=duplicate_id, is_active=True).all()
            existing_main_rel_ids = set(
                await ShopDictRel.filter(shop_id=main_shop_id, is_active=True).values_list("dict_data_id", flat=True)
            )
            for rel in duplicate_rels:
                if rel.dict_data_id in existing_main_rel_ids:
                    await rel.delete()
                else:
                    rel.shop_id = main_shop_id
                    await rel.save()

            # 记录别名
            aliases = main_shop.aliases or []
            if duplicate_shop.name not in aliases:
                aliases.append(duplicate_shop.name)
            if duplicate_shop.aliases:
                for alias in duplicate_shop.aliases:
                    if alias not in aliases:
                        aliases.append(alias)
            main_shop.aliases = aliases

            duplicate_shop.is_active = False
            duplicate_shop.merged_into_id = main_shop_id
            await duplicate_shop.save()

        # 更新主店铺统计值
        main_shop.view_count = main_shop.view_count + view_count_add
        main_shop.favorite_count = await Favorites.filter(shop_id=main_shop_id, is_active=True).count()
        main_shop.comment_count = await Comments.filter(shop_id=main_shop_id, is_active=True).count()
        average_rating = await ShopDAO.calculate_shop_average_rating(main_shop_id)
        main_shop.average_rating = Decimal(str(average_rating))
        await main_shop.save()

        # 记录 main_shop_id 到请求中
        request.proposed_data["main_shop_id"] = main_shop_id
        await request.save()

        # 发送合并通知给反馈用户与收藏用户
        await cls._send_merge_notice(request, main_shop_id, duplicate_shop_ids, admin_id)

    @classmethod
    async def _send_merge_notice(
        cls,
        request: ShopEditRequests,
        main_shop_id: int,
        duplicate_shop_ids: List[int],
        admin_id: int
    ) -> None:
        if not request:
            return

        notified_user_ids = set()
        # 通知反馈发起者
        await MessageDAO.create_user_message(
            recipient_id=request.user_id,
            sender_id=admin_id,
            title="重复店铺合并已完成",
            content=f"您提交的重复店铺反馈已处理，主店铺已合并为ID {main_shop_id}。",
            type="shop_merge",
            related_entity_type="shop_edit_request",
            related_entity_id=request.id
        )
        notified_user_ids.add(request.user_id)

        # 通知收藏了从属店铺的用户
        duplicate_favorites = await Favorites.filter(shop_id__in=duplicate_shop_ids, is_active=True).all()
        for fav in duplicate_favorites:
            if fav.user_id in notified_user_ids:
                continue
            notified_user_ids.add(fav.user_id)
            await MessageDAO.create_user_message(
                recipient_id=fav.user_id,
                sender_id=admin_id,
                title="店铺合并通知",
                content=f"您收藏的店铺已并入主店铺ID {main_shop_id}，请前往新的店铺查看最新信息。",
                type="shop_merge",
                related_entity_type="shop_edit_request",
                related_entity_id=request.id
            )

    @classmethod
    async def _send_edit_request_notification(
        cls,
        request: ShopEditRequests,
        approved: bool,
        admin_id: int,
        reason: Optional[str] = None
    ) -> None:
        if not request:
            return
        title = "店铺编辑申请已处理"
        if approved:
            content = "您提交的店铺编辑申请已通过，管理员已完成处理。"
            if reason:
                content += f" 审核备注：{reason}。"
        else:
            content = f"您提交的店铺编辑申请已被拒绝，原因：{reason or '管理员未填写具体原因'}。"

        await MessageDAO.create_user_message(
            recipient_id=request.user_id,
            sender_id=admin_id,
            title=title,
            content=content,
            type="shop_edit_request",
            related_entity_type="shop_edit_request",
            related_entity_id=request.id
        )

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
        comment_data: CommentCreateRequest
    ) -> CommentResponse:
        """创建评论（纯文字）
        
        Args:
            user_id: 用户ID
            shop_id: 店铺ID
            comment_data: 评论数据请求对象
            
        Returns:
            评论响应对象
        """
        try:
            # 检查店铺是否存在
            shop = await ShopDAO.find_shop_by_id(shop_id)
            if not shop:
                raise ValueError("店铺不存在")
            
            if DEBUG_LOG:
                print(f"DEBUG create_comment: Shop found: {shop.name}")

            # 如果是回复（parent_id > 0），检查父评论是否存在
            if comment_data.parent_id and comment_data.parent_id > 0:
                if DEBUG_LOG:
                    print(f"DEBUG create_comment: Checking parent comment: {comment_data.parent_id}")
                parent = await ShopDAO.get_comment_by_id(comment_data.parent_id)
                if not parent:
                    raise ValueError(f"父评论不存在 (ID: {comment_data.parent_id})")
                if DEBUG_LOG:
                    print(f"DEBUG create_comment: Parent comment found")

            # 创建评论
            comment = await ShopDAO.create_comment(
                shop_id=shop_id,
                user_id=user_id,
                type=comment_data.type,
                content=comment_data.content,
                parent_id=comment_data.parent_id
            )
            
            if DEBUG_LOG:
                print(f"DEBUG create_comment: Comment created: {comment.id}")

            # 获取完整的评论信息（包括用户信息）
            comment_full = await ShopDAO.get_comment_by_id(comment.id)
            
            if DEBUG_LOG:
                print(f"DEBUG create_comment: Comment full data loaded")

            return await cls._build_comment_response(comment_full, user_id)
        except Exception as e:
            if DEBUG_LOG:
                import traceback
                print(f"DEBUG create_comment Error: {str(e)}")
                print(traceback.format_exc())
            raise

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
        try:
            if DEBUG_LOG:
                print(f"DEBUG get_shop_comments service: shop_id={shop_id}, comment_type={comment_type}, current_user_id={current_user_id}")
            
            offset = (page - 1) * page_size
            comments = await ShopDAO.get_shop_comments(
                shop_id=shop_id,
                type=comment_type,
                limit=page_size,
                offset=offset
            )
            
            if DEBUG_LOG:
                print(f"DEBUG get_shop_comments service: Found {len(comments)} comments from DAO")
            
            # 由于 _build_comment_response 是异步方法，需要使用协程列表
            result = await asyncio.gather(*[cls._build_comment_response(c, current_user_id) for c in comments])
            
            if DEBUG_LOG:
                print(f"DEBUG get_shop_comments service: Built {len(result)} comment responses")
            
            return result
        except Exception as e:
            if DEBUG_LOG:
                import traceback
                print(f"DEBUG get_shop_comments service Error: {str(e)}")
                print(traceback.format_exc())
            raise

    @classmethod
    async def get_comment_replies(
        cls,
        comment_id: int,
        current_user_id: Optional[int] = None
    ) -> List[CommentResponse]:
        """获取评论的子回复列表"""
        replies = await ShopDAO.get_comment_replies(comment_id)
        return await asyncio.gather(*[cls._build_comment_response(r, current_user_id) for r in replies])

    @classmethod
    async def update_comment(
        cls,
        user_id: int,
        comment_id: int,
        content: str
    ) -> CommentResponse:
        """更新评论（仅作者可更新）"""
        comment = await ShopDAO.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("评论不存在")
        if comment.user_id != user_id:
            raise ValueError("无权修改他人评论")

        updated_comment = await ShopDAO.update_comment(comment_id, content)
        return await cls._build_comment_response(updated_comment, user_id)

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
    async def _build_comment_response(
        cls,
        comment: Comments,
        current_user_id: Optional[int] = None
    ) -> CommentResponse:
        """构建评论响应（包含嵌套回复）"""
        try:
            if DEBUG_LOG:
                print(f"DEBUG _build_comment_response: Building response for comment {comment.id}")
            
            has_liked = False
            if current_user_id:
                # 同步检查点赞状态，这里简化处理
                pass

            # 构建用户信息
            # Tortoise ORM 中，如果预加载了 user，comment.user 是一个 Users 对象；
            # 否则 comment.user_id 直接是 ID。通过 hasattr 检查 user_id 是否存在。
            user = None
            if hasattr(comment, 'user') and comment.user is not None:
                # 如果 user 被预加载了，直接使用
                if DEBUG_LOG:
                    print(f"DEBUG _build_comment_response: User preloaded for comment {comment.id}")
                user = CommentUserResponse(
                    id=comment.user.id,
                    username=comment.user.username,
                    avatar=comment.user.avatar
                )
            elif hasattr(comment, 'user_id') and comment.user_id:
                # 否则使用 user_id 查询用户（异步）
                if DEBUG_LOG:
                    print(f"DEBUG _build_comment_response: Querying user for comment {comment.id}, user_id={comment.user_id}")
                user_obj = await Users.get_or_none(id=comment.user_id, is_active=True)
                if user_obj:
                    user = CommentUserResponse(
                        id=user_obj.id,
                        username=user_obj.username,
                        avatar=user_obj.avatar
                    )
                if DEBUG_LOG:
                    print(f"DEBUG _build_comment_response: User found={user_obj is not None} for comment {comment.id}")

            # 构建评论关联的图片列表（直接查询 Images 表）
            images = []
            if hasattr(comment, 'id') and comment.id:
                if DEBUG_LOG:
                    print(f"DEBUG _build_comment_response: Querying images for comment {comment.id}")
                # Tortoise ORM 中 ReverseRelation 需要通过查询 Images 表获取
                images_list = await Images.filter(
                    entity_type="comment",
                    entity_id=comment.id,
                    is_active=True
                ).all()
                if DEBUG_LOG:
                    print(f"DEBUG _build_comment_response: Found {len(images_list)} images for comment {comment.id}")
                for img in images_list:
                    images.append(CommentImageResponse(
                        id=img.id,
                        url=img.url,
                        created_at=img.created_at
                    ))
            
            if DEBUG_LOG:
                print(f"DEBUG _build_comment_response: Built response for comment {comment.id}, user={user is not None}, images={len(images)}")

            return CommentResponse(
                id=comment.id,
                shop_id=comment.shop_id,
                user=user,
                type=comment.type,
                parent_id=comment.parent_id,
                content=comment.content,
                like_count=comment.like_count,
                reply_count=comment.reply_count,
                images=images,
                has_liked=has_liked,
                created_at=comment.created_at,
                updated_at=comment.updated_at
            )
        except Exception as e:
            if DEBUG_LOG:
                import traceback
                print(f"DEBUG _build_comment_response Error for comment {comment.id}: {str(e)}")
                print(traceback.format_exc())
            raise

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
