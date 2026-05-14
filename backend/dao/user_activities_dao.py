from typing import Optional, List
from models.users import Activities
from models.shops import Shops, Comments
from models.users import Favorites
from models.logs import UserBehaviorLogs


class UserActivitiesDAO:
    """用户动态数据访问层"""

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

    @classmethod
    async def get_user_activities(
        cls,
        user_id: int,
        type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Activities]:
        """
        获取用户动态列表（按时间倒序）
        
        Args:
            user_id: 用户ID
            type: 活动类型（可选）
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            活动记录列表（不包含关联详情）
        """
        query = Activities.filter(
            user_id=user_id, 
            is_active=True
        ).order_by("-created_at")
        
        if type:
            query = query.filter(type=type)
            
        return await query.limit(limit).offset(offset).all()

    @classmethod
    async def get_activity_by_id(cls, activity_id: int) -> Optional[Activities]:
        """
        根据ID获取动态
        
        Args:
            activity_id: 动态ID
            
        Returns:
            活动记录对象，不存在则返回 None
        """
        return await Activities.get_or_none(id=activity_id, is_active=True)

    @classmethod
    async def get_user_activity_count(cls, user_id: int) -> int:
        """
        获取用户动态总数
        
        Args:
            user_id: 用户ID
            
        Returns:
            动态总数
        """
        return await Activities.filter(user_id=user_id, is_active=True).count()

    @classmethod
    async def get_user_activities_with_details(
        cls,
        user_id: int,
        type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[dict]:
        """
        获取用户动态列表（包含关联详情）
        
        Args:
            user_id: 用户ID
            type: 活动类型（可选）
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            包含详情的动态列表
        """
        activities = await cls.get_user_activities(user_id, type, limit, offset)
        result = []
        
        for activity in activities:
            detail = await cls._get_activity_detail(activity)
            if detail:
                result.append(detail)
                
        return result

    @classmethod
    async def _get_activity_detail(cls, activity: Activities) -> Optional[dict]:
        """
        获取单条动态的详细信息
        
        Args:
            activity: 活动记录对象
            
        Returns:
            包含详情的字典
        """
        detail = {
            "id": activity.id,
            "user_id": activity.user_id,
            "type": activity.type,
            "target_type": activity.target_type,
            "target_id": activity.target_id,
            "content": activity.content,
            "created_at": activity.created_at,
            "target_detail": None
        }
        
        # 根据 target_type 获取关联详情
        if activity.target_type == "shop":
            detail["target_detail"] = await cls._get_shop_detail(activity.target_id)
        elif activity.target_type == "comment":
            detail["target_detail"] = await cls._get_comment_detail(activity.target_id)
        elif activity.target_type == "comment_like":
            detail["target_detail"] = await cls._get_comment_like_detail(activity.target_id)
        elif activity.target_type == "rating":
            detail["target_detail"] = await cls._get_rating_detail(activity.target_id)
        elif activity.target_type == "favorite":
            detail["target_detail"] = await cls._get_favorite_detail(activity.target_id)
            
        return detail

    @classmethod
    async def _get_shop_detail(cls, shop_id: int) -> Optional[dict]:
        """获取店铺详情"""
        shop = await Shops.get_or_none(id=shop_id, is_active=True)
        if not shop:
            return None
        return {
            "shop_id": shop.id,
            "shop_name": shop.name,
            "shop_url": f"/shop/{shop.id}",
            "description": shop.description,
            "average_rating": float(shop.average_rating) if shop.average_rating else 0.0
        }

    @classmethod
    async def _get_comment_detail(cls, comment_id: int) -> Optional[dict]:
        """获取评论详情"""
        comment = await Comments.get_or_none(id=comment_id, is_active=True).select_related("shop", "user")
        if not comment:
            return None
        return {
            "comment_id": comment.id,
            "content": comment.content[:50] + "..." if len(comment.content) > 50 else comment.content,
            "shop_id": comment.shop_id,
            "shop_name": comment.shop.name if comment.shop else "未知店铺",
            "shop_url": f"/shop/{comment.shop_id}" if comment.shop else None
        }

    @classmethod
    async def _get_comment_like_detail(cls, like_id: int) -> Optional[dict]:
        """获取评论点赞详情"""
        from models.shops import CommentsLikes
        
        like_record = await CommentsLikes.get_or_none(id=like_id, is_active=True).select_related("comment").prefetch_related("comment__shop")
        if not like_record or not like_record.comment:
            return None
        
        comment = like_record.comment
        return {
            "like_id": like_record.id,
            "comment_id": comment.id,
            "content": comment.content[:50] + "..." if len(comment.content) > 50 else comment.content,
            "shop_id": comment.shop_id,
            "shop_name": comment.shop.name if comment.shop else "未知店铺",
            "shop_url": f"/shop/{comment.shop_id}" if comment.shop else None
        }

    @classmethod
    async def _get_rating_detail(cls, rating_id: int) -> Optional[dict]:
        """获取评分详情"""
        from models.shops import Ratings
        
        rating = await Ratings.get_or_none(id=rating_id, is_active=True).select_related("shop")
        if not rating or not rating.shop:
            return None
        return {
            "rating_id": rating.id,
            "score": rating.score,
            "shop_id": rating.shop.id,
            "shop_name": rating.shop.name,
            "shop_url": f"/shop/{rating.shop.id}"
        }

    @classmethod
    async def _get_favorite_detail(cls, favorite_id: int) -> Optional[dict]:
        """获取收藏详情"""
        from models.users import Favorites
        
        favorite = await Favorites.get_or_none(id=favorite_id, is_active=True).select_related("shop")
        if not favorite or not favorite.shop:
            return None
        return {
            "favorite_id": favorite.id,
            "shop_id": favorite.shop.id,
            "shop_name": favorite.shop.name,
            "shop_url": f"/shop/{favorite.shop.id}"
        }
