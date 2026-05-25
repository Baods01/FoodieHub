from typing import Optional
from models.users import Activities
from models.shops import Shops, Comments, Ratings
from models.users import Favorites, Users
from dao.user_activities_dao import UserActivitiesDAO


class UserActivitiesService:
    """用户动态服务层"""

    @classmethod
    async def get_user_activities(
        cls,
        user_id: int,
        type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> dict:
        """
        获取用户动态列表
        
        Args:
            user_id: 用户ID
            type: 活动类型（可选）
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            包含动态列表和分页信息的字典
        """
        # 获取动态总数
        total = await UserActivitiesDAO.get_user_activity_count(user_id)
        
        # 获取动态详情
        activities = await UserActivitiesDAO.get_user_activities_with_details(
            user_id, type, limit, offset
        )
        
        return {
            "items": activities,
            "total": total,
            "has_more": (offset + len(activities)) < total
        }

    @classmethod
    async def create_rating_activity(cls, user_id: int, shop_id: int, score: int) -> Activities:
        """
        创建评分动态
        
        Args:
            user_id: 用户ID
            shop_id: 店铺ID
            score: 评分
            
        Returns:
            创建的活动记录
        """
        # 获取店铺名称
        shop = await Shops.get_or_none(id=shop_id, is_active=True)
        if not shop:
            return None
            
        content = f"评分了 {shop.name} ({score}星)"
        
        return await UserActivitiesDAO.create_activity(
            user_id=user_id,
            type="rating",
            target_id=shop_id,
            target_type="shop",
            content=content
        )

    @classmethod
    async def create_comment_activity(cls, user_id: int, comment_id: int, shop_id: int) -> Activities:
        """
        创建评论动态
        
        Args:
            user_id: 用户ID
            comment_id: 评论ID
            shop_id: 店铺ID
            
        Returns:
            创建的活动记录
        """
        # 获取店铺名称
        shop = await Shops.get_or_none(id=shop_id, is_active=True)
        shop_name = shop.name if shop else "店铺"
        
        content = f"评论了 {shop_name}"
        
        return await UserActivitiesDAO.create_activity(
            user_id=user_id,
            type="comment",
            target_id=comment_id,
            target_type="comment",
            content=content
        )

    @classmethod
    async def create_like_activity(cls, user_id: int, comment_id: int) -> Activities:
        """
        创建点赞动态
        
        Args:
            user_id: 用户ID
            comment_id: 评论ID
            
        Returns:
            创建的活动记录
        """
        # 获取评论详情（预加载 shop 关联）
        comment = await Comments.get_or_none(id=comment_id, is_active=True).select_related("shop")
        if not comment:
            return None
            
        # 获取店铺名称
        shop_name = comment.shop.name if comment.shop else "店铺"
        
        content = f"点赞了在 {shop_name} 的评论"
        
        return await UserActivitiesDAO.create_activity(
            user_id=user_id,
            type="like",
            target_id=comment_id,
            target_type="comment_like",
            content=content
        )

    @classmethod
    async def create_favorite_activity(cls, user_id: int, shop_id: int) -> Activities:
        """
        创建收藏动态
        
        Args:
            user_id: 用户ID
            shop_id: 店铺ID
            
        Returns:
            创建的活动记录
        """
        # 获取店铺名称
        shop = await Shops.get_or_none(id=shop_id, is_active=True)
        if not shop:
            return None
            
        content = f"收藏了 {shop.name}"
        
        return await UserActivitiesDAO.create_activity(
            user_id=user_id,
            type="favorite",
            target_id=shop_id,
            target_type="favorite",
            content=content
        )

    @classmethod
    async def delete_activity(cls, activity_id: int) -> bool:
        """
        软删除活动记录
        
        Args:
            activity_id: 活动记录ID
            
        Returns:
            True表示删除成功
        """
        activity = await UserActivitiesDAO.get_activity_by_id(activity_id)
        if activity:
            activity.is_active = False
            await activity.save()
            return True
        return False