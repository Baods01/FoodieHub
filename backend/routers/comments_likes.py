from fastapi import APIRouter, Depends, HTTPException

from dependencies.auth import oauth2_scheme, get_current_user
from schemas.comments_likes import CommentLikeCreate, CommentLikeResponse
from services.comments_likes_service import CommentsLikesService
from schemas.users import UserResponse

router = APIRouter()


@router.post("/comments/like", summary="点赞/取消点赞评论")
async def toggle_comment_like(
    like_data: CommentLikeCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    点赞/取消点赞评论
    
    - **comment_id**: 评论ID
    - 同一用户对同一条评论可以多次点赞/取消点赞
    - 首次点赞时会向评论作者发送通知
    """
    if current_user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        user_id = current_user.id
        comment_id = like_data.comment_id
        
        # 切换点赞状态
        result = await CommentsLikesService.toggle_like(user_id, comment_id)
        
        return {
            "code": 200,
            "msg": "操作成功",
            "data": {
                "is_liked": result["is_liked"],
                "like_count": result["like_count"]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/comments/{comment_id}/like-count", summary="获取评论点赞数")
async def get_comment_like_count(comment_id: int):
    """
    获取评论的点赞数
    
    - **comment_id**: 评论ID
    """
    try:
        like_count = await CommentsLikesService.get_like_count(comment_id)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "comment_id": comment_id,
                "like_count": like_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/comments/likes/my", summary="获取我的点赞列表")
async def get_my_likes(
    current_user: UserResponse = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """
    获取当前用户的点赞记录列表
    
    - **limit**: 每页数量
    - **offset**: 偏移量
    """
    if current_user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        from dao.comments_likes_dao import CommentsLikesDAO
        
        user_id = current_user.id
        likes = await CommentsLikesDAO.get_user_likes(user_id, limit, offset)
        
        data = [
            {
                "id": like.id,
                "comment_id": like.comment_id,
                "user_id": like.user_id,
                "created_at": like.created_at.isoformat() if like.created_at else None,
                "comment_content": like.comment.content if like.comment else None,
                "comment_user": {
                    "id": like.comment.user.id if like.comment and like.comment.user else None,
                    "username": like.comment.user.username if like.comment and like.comment.user else None
                } if like.comment else None
            }
            for like in likes
        ]
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "items": data,
                "total": len(data)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")