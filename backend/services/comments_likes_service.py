from typing import Optional
from models.users import Users, Messages
from models.shops import Comments

from dao.message_dao import MessageDAO
from dao.comments_likes_dao import CommentsLikesDAO
from services.user_activities_service import UserActivitiesService


class CommentsLikesService:
    """评论点赞服务层"""

    @classmethod
    async def toggle_like(cls, user_id: int, comment_id: int) -> dict:
        """
        切换点赞状态（点赞/取消点赞）
        
        Args:
            user_id: 用户ID
            comment_id: 评论ID
            
        Returns:
            包含点赞状态和新点赞数的字典
        """
        # 验证评论是否存在
        comment = await CommentsLikesDAO.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("评论不存在")
        
        # 检查用户是否存在
        user = await Users.get_or_none(id=user_id, is_active=True)
        if not user:
            raise ValueError("用户不存在")
        
        # 切换点赞状态
        is_liked = await CommentsLikesDAO.toggle_like(user_id, comment_id)
        
        # 获取新的点赞数
        like_count = await CommentsLikesDAO.get_like_count(comment_id)
        
        # 首次点赞时发送通知和生成动态
        if is_liked:
            await cls.send_like_notification(comment_id, user_id)
            # 创建点赞动态
            await UserActivitiesService.create_like_activity(user_id, comment_id)
        
        return {
            "is_liked": is_liked,
            "like_count": like_count
        }

    @classmethod
    async def send_like_notification(cls, comment_id: int, user_id: int) -> None:
        """
        首次点赞时向评论作者发送通知
        
        Args:
            comment_id: 评论ID
            user_id: 点赞用户ID
        """
        # 获取评论详情（预加载 user 关联）
        comment = await Comments.get_or_none(id=comment_id, is_active=True).select_related("user")
        if not comment:
            return
        
        # 获取点赞用户
        like_user = await Users.get_or_none(id=user_id)
        if not like_user:
            return
        
        # 获取评论作者
        author = comment.user
        if not author:
            return
        
        # 避免给自己点赞发送通知
        if author.id == user_id:
            return
        
        # 发送系统消息
        await MessageDAO.create_user_message(
            recipient_id=author.id,
            sender_id=user_id,
            title=f"您的评论获得了点赞",
            content=f"用户 {like_user.username} 点赞了您的评论：{comment.content[:50]}{'...' if len(comment.content) > 50 else ''}",
            type="comment_like",
            related_entity_type="comment",
            related_entity_id=comment_id
        )

    @classmethod
    async def check_like(cls, user_id: int, comment_id: int) -> bool:
        """
        检查用户是否已点赞评论
        
        Args:
            user_id: 用户ID
            comment_id: 评论ID
            
        Returns:
            True表示已点赞，False表示未点赞
        """
        return await CommentsLikesDAO.check_like(user_id, comment_id)

    @classmethod
    async def get_like_count(cls, comment_id: int) -> int:
        """
        获取评论的点赞数
        
        Args:
            comment_id: 评论ID
            
        Returns:
            点赞数量
        """
        return await CommentsLikesDAO.get_like_count(comment_id)