"""检查点赞记录详情"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tortoise import Tortoise
from models.shops import Comments, CommentsLikes


async def check_likes():
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
    print("所有点赞记录详情")
    print("=" * 60)
    
    likes = await CommentsLikes.all().order_by("-id")
    
    for like in likes:
        comment = await Comments.get_or_none(id=like.comment_id)
        comment_info = f"评论ID={like.comment_id}" if comment else f"评论ID={like.comment_id}(不存在)"
        print(f"\nlike_id={like.id}, user_id={like.user_id}, {comment_info}")
        print(f"  is_active={like.is_active}, created_at={like.created_at}")
    
    print("\n" + "=" * 60)
    print("评论点赞数对比")
    print("=" * 60)
    
    comments = await Comments.all().order_by("-id")
    for comment in comments:
        # 实际有效的点赞数
        actual_count = await CommentsLikes.filter(
            comment_id=comment.id,
            is_active=True
        ).count()
        
        # 评论显示的点赞数
        displayed_count = comment.like_count
        
        print(f"\n评论 {comment.id}:")
        print(f"  显示点赞数: {displayed_count}")
        print(f"  实际有效点赞数: {actual_count}")
        
        if displayed_count != actual_count:
            print(f"  ⚠️ 点赞数不一致！")
        else:
            print(f"  ✓ 点赞数一致")
    
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(check_likes())