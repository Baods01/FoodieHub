"""检查数据库中的评论"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from tortoise import Tortoise
from models.shops import Comments


async def check_comments():
    """检查评论"""
    
    await Tortoise.init(
        config={
            "connections": {
                "default": "mysql://root:123456@localhost:3306/foodie_hub"
            },
            "apps": {
                "models": {
                    "models": ["models"],
                    "default_connection": "default",
                },
            },
        }
    )
    await Tortoise.generate_schemas()
    
    print("=" * 60)
    print("数据库中的评论列表")
    print("=" * 60)
    
    # 获取所有评论
    comments = await Comments.all().order_by("-id").limit(10)
    
    if not comments:
        print("\n没有找到任何评论！")
        return
    
    for comment in comments:
        print(f"\n评论 ID: {comment.id}")
        print(f"  内容: {comment.content[:50]}...")
        print(f"  点赞数: {comment.like_count}")
        print(f"  is_active: {comment.is_active}")
        print(f"  created_at: {comment.created_at}")
    
    # 检查点赞记录
    print("\n" + "=" * 60)
    print("点赞记录统计")
    print("=" * 60)
    
    from models.shops import CommentsLikes
    
    # 总点赞数
    total_likes = await CommentsLikes.all().count()
    active_likes = await CommentsLikes.filter(is_active=True).count()
    inactive_likes = await CommentsLikes.filter(is_active=False).count()
    
    print(f"\n总点赞记录数: {total_likes}")
    print(f"  有效的 (is_active=True): {active_likes}")
    print(f"  软删除的 (is_active=False): {inactive_likes}")
    
    # 检查某条评论的具体点赞记录
    if comments:
        first_comment = comments[0]
        print(f"\n评论 {first_comment.id} 的点赞记录:")
        likes = await CommentsLikes.filter(comment_id=first_comment.id).all()
        for like in likes:
            print(f"  * like_id={like.id}, user_id={like.user_id}, is_active={like.is_active}")
    
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(check_comments())