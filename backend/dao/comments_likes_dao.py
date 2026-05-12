from typing import Optional
from models.shops import Comments, CommentsLikes


class CommentsLikesDAO:
    """评论点赞数据访问层"""

    @classmethod
    async def toggle_like(cls, user_id: int, comment_id: int) -> bool:
        """
        切换点赞状态（点赞/取消点赞）
        
        Args:
            user_id: 用户ID
            comment_id: 评论ID
            
        Returns:
            True表示点赞，False表示取消点赞
        """
        # 查询当前点赞记录
        like = await CommentsLikes.get_or_none(
            user_id=user_id, 
            comment_id=comment_id, 
            is_active=True
        )
        
        if like:
            # 已点赞，执行取消点赞
            await like.delete()
            # 减少点赞数
            comment = await Comments.get_or_none(id=comment_id)
            if comment and comment.like_count > 0:
                comment.like_count -= 1
                await comment.save()
            return False
        else:
            # 未点赞，执行点赞
            await CommentsLikes.create(
                user_id=user_id,
                comment_id=comment_id
            )
            # 增加点赞数
            comment = await Comments.get_or_none(id=comment_id)
            if comment:
                comment.like_count += 1
                await comment.save()
            return True

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
        return await CommentsLikes.filter(
            user_id=user_id,
            comment_id=comment_id,
            is_active=True
        ).exists()

    @classmethod
    async def get_like_count(cls, comment_id: int) -> int:
        """
        获取评论的点赞数
        
        Args:
            comment_id: 评论ID
            
        Returns:
            点赞数量
        """
        return await CommentsLikes.filter(
            comment_id=comment_id,
            is_active=True
        ).count()

    @classmethod
    async def get_comment_by_id(cls, comment_id: int) -> Optional[Comments]:
        """
        根据ID获取评论
        
        Args:
            comment_id: 评论ID
            
        Returns:
            评论对象，不存在则返回 None
        """
        return await Comments.get_or_none(id=comment_id, is_active=True)

    @classmethod
    async def get_user_likes(cls, user_id: int, limit: int = 20, offset: int = 0):
        """
        获取用户的点赞记录
        
        Args:
            user_id: 用户ID
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            点赞记录列表
        """
        return await CommentsLikes.filter(
            user_id=user_id,
            is_active=True
        ).order_by("-created_at").limit(limit).offset(offset).prefetch_related("comment").all()