from typing import Optional, List, Dict, Any
import logging

from models.shops import Comments, CommentsLikes
from utils.logger import log_like_action



class CommentsLikesDAO:
    """评论点赞数据访问层"""

    @classmethod
    async def toggle_like(cls, user_id: int, comment_id: int) -> bool:
        """
        切换点赞状态（点赞/取消点赞）
        - 动态记录由 CommentsLikesService.create_like_activity 创建
        
        Args:
            user_id: 用户ID
            comment_id: 评论ID
            
        Returns:
            True表示点赞，False表示取消点赞
        """
        try:
            # 记录开始
            log_like_action("toggle_start", user_id=user_id, comment_id=comment_id, details={"step": "start"})
            
            # 查询当前有效的点赞记录（is_active=True）
            like = await CommentsLikes.get_or_none(
                user_id=user_id, 
                comment_id=comment_id, 
                is_active=True
            )
            
            if like:
                # 已点赞，执行取消点赞（软删除）
                log_like_action("already_liked", user_id=user_id, comment_id=comment_id, details={
                    "like_id": like.id,
                    "created_at": like.created_at.isoformat() if like.created_at else None,
                    "step": "cancel_like"
                })
                
                like.is_active = False
                await like.save()
                
                # 减少点赞数
                comment = await Comments.get_or_none(id=comment_id)
                if comment:
                    if comment.like_count > 0:
                        comment.like_count -= 1
                        log_like_action("totalCount_decremented", user_id=user_id, comment_id=comment_id, details={
                            "old_count": comment.like_count + 1,
                            "new_count": comment.like_count
                        })
                    else:
                        log_like_action(" totalCount_no_decrement", user_id=user_id, comment_id=comment_id, details={
                            "current_count": comment.like_count,
                            "reason": "count already 0 or negative"
                        })
                    await comment.save()
                else:
                    log_like_action("comment_not_found", user_id=user_id, comment_id=comment_id, details={"step": "update_count_after_cancel"})
                
                return False
            else:
                # 未点赞，执行点赞
                log_like_action("not_liked_yet", user_id=user_id, comment_id=comment_id, details={"step": "try_to_like"})
                
                # 先检查是否存在已软删除的记录，如果有则恢复
                old_like = await CommentsLikes.get_or_none(
                    user_id=user_id, 
                    comment_id=comment_id
                )
                
                if old_like:
                    log_like_action("found_soft_deleted_record", user_id=user_id, comment_id=comment_id, details={
                        "old_like_id": old_like.id,
                        "old_is_active": old_like.is_active,
                        "created_at": old_like.created_at.isoformat() if old_like.created_at else None,
                        "step": "recover_old_record"
                    })
                    
                    # 恢复旧的点赞记录
                    old_like.is_active = True
                    await old_like.save()
                    
                    # 增加点赞数
                    comment = await Comments.get_or_none(id=comment_id)
                    if comment:
                        comment.like_count += 1
                        log_like_action("totalCount_incremented", user_id=user_id, comment_id=comment_id, details={
                            "old_count": comment.like_count - 1,
                            "new_count": comment.like_count
                        })
                        await comment.save()
                    else:
                        log_like_action("comment_not_found", user_id=user_id, comment_id=comment_id, details={"step": "update_count_after_recover"})
                else:
                    log_like_action("no_soft_deleted_record", user_id=user_id, comment_id=comment_id, details={"step": "create_new_record"})
                    
                    # 创建新的点赞记录
                    new_like = await CommentsLikes.create(
                        user_id=user_id,
                        comment_id=comment_id,
                        is_active=True
                    )
                    log_like_action("new_record_created", user_id=user_id, comment_id=comment_id, details={
                        "new_like_id": new_like.id,
                        "created_at": new_like.created_at.isoformat() if new_like.created_at else None
                    })
                    
                    # 增加点赞数
                    comment = await Comments.get_or_none(id=comment_id)
                    if comment:
                        comment.like_count += 1
                        log_like_action("totalCount_incremented", user_id=user_id, comment_id=comment_id, details={
                            "old_count": comment.like_count - 1,
                            "new_count": comment.like_count
                        })
                        await comment.save()
                    else:
                        log_like_action("comment_not_found", user_id=user_id, comment_id=comment_id, details={"step": "update_count_after_create"})
                
                return True
                
        except Exception as e:
            # 记录错误
            log_like_action("error", user_id=user_id, comment_id=comment_id, details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "step": "exception"
            })
            raise

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
        return await Comments.get_or_none(id=comment_id, is_active=True).select_related("user")

    @classmethod
    async def get_user_likes(cls, user_id: int, limit: int = 20, offset: int = 0) -> List[CommentsLikes]:
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
        ).order_by("-created_at").limit(limit).offset(offset).select_related(
            "comment",
            "comment__user"
        ).all()

    @classmethod
    async def get_like_by_id(cls, like_id: int) -> Optional[CommentsLikes]:
        """
        根据ID获取点赞记录
        
        Args:
            like_id: 点赞记录ID
            
        Returns:
            点赞记录对象，不存在则返回 None
        """
        return await CommentsLikes.get_or_none(id=like_id, is_active=True)

    @classmethod
    async def get_user_likes_count(cls, user_id: int) -> int:
        """
        获取用户点赞总数
        
        Args:
            user_id: 用户ID
            
        Returns:
            点赞总数
        """
        return await CommentsLikes.filter(user_id=user_id, is_active=True).count()
