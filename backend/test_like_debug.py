"""点赞功能调试测试脚本"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from tortoise import Tortoise
from models.shops import Comments, CommentsLikes
from dao.comments_likes_dao import CommentsLikesDAO


async def test_like_function():
    """测试点赞功能"""
    
    # 初始化数据库连接
    await Tortoise.init(
        config={
            "connections": {
                "default": "mysql://root:123456@localhost:3306/foodie_hub"
            },
            "apps": {
                "models": {
                    "models": ["models", "aerich.models"],
                    "default_connection": "default",
                },
            },
        }
    )
    await Tortoise.generate_schemas()
    
    print("=" * 60)
    print("点赞功能调试测试")
    print("=" * 60)
    
    # 测试数据
    test_user_id = 1  # 替换为实际测试用户ID
    test_comment_id = 1  # 替换为实际测试评论ID
    
    # 1. 检查评论是否存在
    print("\n1. 检查评论是否存在...")
    comment = await Comments.get_or_none(id=test_comment_id, is_active=True)
    if not comment:
        print(f"   ⚠️ 评论 {test_comment_id} 不存在或已被删除")
        return
    print(f"   ✓ 评论 {test_comment_id} 存在")
    print(f"   - 评论内容: {comment.content[:50]}...")
    print(f"   - 当前点赞数: {comment.like_count}")
    
    # 2. 检查用户是否存在
    print(f"\n2. 检查用户 {test_user_id} 是否存在...")
    from models.users import Users
    user = await Users.get_or_none(id=test_user_id, is_active=True)
    if not user:
        print(f"   ⚠️ 用户 {test_user_id} 不存在或已被删除")
        return
    print(f"   ✓ 用户 {test_user_id} 存在")
    print(f"   - 用户名: {user.username}")
    
    # 3. 检查当前点赞状态
    print(f"\n3. 检查用户 {test_user_id} 对评论 {test_comment_id} 的点赞状态...")
    
    # 检查有效的点赞记录
    active_like = await CommentsLikes.get_or_none(
        user_id=test_user_id,
        comment_id=test_comment_id,
        is_active=True
    )
    print(f"   - 有效的点赞记录 (is_active=True): {active_like.id if active_like else '无'}")
    
    # 检查所有点赞记录（包括软删除的）
    all_likes = await CommentsLikes.filter(
        user_id=test_user_id,
        comment_id=test_comment_id
    ).all()
    print(f"   - 所有点赞记录（含软删除）: {len(all_likes)} 条")
    for like in all_likes:
        print(f"     * ID={like.id}, is_active={like.is_active}, created_at={like.created_at}")
    
    # 4. 执行点赞切换
    print(f"\n4. 执行点赞切换操作...")
    try:
        result = await CommentsLikesDAO.toggle_like(test_user_id, test_comment_id)
        print(f"   ✓ 点赞操作完成: {result}")
        
        # 5. 验证结果
        print(f"\n5. 验证结果...")
        
        # 重新获取评论
        comment_new = await Comments.get_or_none(id=test_comment_id)
        if comment_new:
            print(f"   - 评论新点赞数: {comment_new.like_count}")
        
        # 重新检查点赞状态
        active_like_new = await CommentsLikes.get_or_none(
            user_id=test_user_id,
            comment_id=test_comment_id,
            is_active=True
        )
        print(f"   - 有效的点赞记录: {active_like_new.id if active_like_new else '无'}")
        
        # 检查所有记录
        all_likes_new = await CommentsLikes.filter(
            user_id=test_user_id,
            comment_id=test_comment_id
        ).all()
        print(f"   - 所有点赞记录（含软删除）: {len(all_likes_new)} 条")
        for like in all_likes_new:
            print(f"     * ID={like.id}, is_active={like.is_active}, created_at={like.created_at}")
        
    except Exception as e:
        print(f"   ✗ 操作失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. 显示日志文件位置
    print("\n" + "=" * 60)
    print("日志文件路径: FoodieHub/backend/logs/debug_*.log")
    print("请查看日志文件了解详细的调试信息")
    print("=" * 60)
    
    # 关闭数据库连接
    await Tortoise.close_connections()


if __name__ == "__main__":
    print("开始测试点赞功能...")
    asyncio.run(test_like_function())