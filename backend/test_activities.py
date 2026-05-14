#!/usr/bin/env python
"""测试动态记录功能"""

import asyncio
from models.users import Users, Activities
from models.shops import Shops, Ratings, Comments, CommentsLikes
from models.dict import DictTypes, DictData
from models.base import BaseModel
from tortoise import Tortoise


async def init_db():
    """初始化数据库连接"""
    await Tortoise.init(
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.sqlite",
                    "credentials": {
                        "file": "db.sqlite3",
                    },
                },
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


async def close_db():
    """关闭数据库连接"""
    await Tortoise.close_connections()


async def test_rating_activity():
    """测试评分动态记录"""
    print("\n=== 测试评分动态记录 ===")
    # 获取测试用户和店铺
    user = await Users.get_or_none(id=1, is_active=True)
    shop = await Shops.get_or_none(id=1, is_active=True)
    
    if not user or not shop:
        print("跳过：需要用户ID=1和店铺ID=1进行测试")
        return
    
    # 执行评分
    from dao.shop_dao import ShopDAO
    rating = await ShopDAO.create_or_update_rating(user.id, shop.id, 5)
    print(f"评分成功: {rating.id}")
    
    # 检查动态是否创建
    activities = await Activities.filter(type="rating", user_id=user.id, target_id=shop.id).all()
    if activities:
        print(f"✓ 评分动态创建成功: {activities[0].content}")
    else:
        print("✗ 评分动态未创建")


async def test_comment_activity():
    """测试评论动态记录"""
    print("\n=== 测试评论动态记录 ===")
    # 获取测试用户和店铺
    user = await Users.get_or_none(id=1, is_active=True)
    shop = await Shops.get_or_none(id=1, is_active=True)
    
    if not user or not shop:
        print("跳过：需要用户ID=1和店铺ID=1进行测试")
        return
    
    # 执行评论
    from dao.shop_dao import ShopDAO
    comment = await ShopDAO.create_comment(shop.id, user.id, "这是一家很棒的店铺！")
    print(f"评论成功: {comment.id}")
    
    # 检查动态是否创建
    activities = await Activities.filter(type="comment", user_id=user.id, target_id=comment.id).all()
    if activities:
        print(f"✓ 评论动态创建成功: {activities[0].content}")
    else:
        print("✗ 评论动态未创建")


async def test_like_activity():
    """测试点赞动态记录"""
    print("\n=== 测试点赞动态记录 ===")
    # 获取测试用户和评论
    user = await Users.get_or_none(id=2, is_active=True)
    comment = await Comments.get_or_none(id=1, is_active=True)
    
    if not user or not comment:
        print("跳过：需要用户ID=2和评论ID=1进行测试")
        return
    
    # 执行点赞
    from dao.comments_likes_dao import CommentsLikesDAO
    is_liked = await CommentsLikesDAO.toggle_like(user.id, comment.id)
    print(f"点赞状态: {is_liked}")
    
    # 检查动态是否创建
    activities = await Activities.filter(type="like", user_id=user.id, target_id=comment.id).all()
    if activities:
        print(f"✓ 点赞动态创建成功: {activities[0].content}")
    else:
        print("✗ 点赞动态未创建")


async def test_favorite_activity():
    """测试收藏动态记录"""
    print("\n=== 测试收藏动态记录 ===")
    # 获取测试用户和店铺
    user = await Users.get_or_none(id=3, is_active=True)
    shop = await Shops.get_or_none(id=1, is_active=True)
    
    if not user or not shop:
        print("跳过：需要用户ID=3和店铺ID=1进行测试")
        return
    
    # 执行收藏
    from dao.shop_dao import ShopDAO
    favorite = await ShopDAO.create_favorite(user.id, shop.id)
    print(f"收藏成功: {favorite.id}")
    
    # 检查动态是否创建
    activities = await Activities.filter(type="favorite", user_id=user.id, target_id=shop.id).all()
    if activities:
        print(f"✓ 收藏动态创建成功: {activities[0].content}")
    else:
        print("✗ 收藏动态未创建")


async def test_get_my_activities():
    """测试获取我的动态列表"""
    print("\n=== 测试获取我的动态列表 ===")
    user = await Users.get_or_none(id=1, is_active=True)
    
    if not user:
        print("跳过：需要用户ID=1进行测试")
        return
    
    from services.user_activities_service import UserActivitiesService
    activities = await UserActivitiesService.get_user_activities(user.id)
    
    print(f"用户 '{user.username}' 的动态列表:")
    for item in activities["items"]:
        print(f"  - {item['type']}: {item['content']}")
    
    print(f"\n总数: {activities['total']}, 是否有更多: {activities['has_more']}")


async def main():
    """主测试函数"""
    print("=" * 60)
    print("动态记录功能测试")
    print("=" * 60)
    
    # 确保数据库已初始化
    print("\n正在进行数据库查询测试...")
    
    try:
        await test_rating_activity()
        await test_comment_activity()
        await test_like_activity()
        await test_favorite_activity()
        await test_get_my_activities()
        
        print("\n" + "=" * 60)
        print("测试完成！请检查上述输出结果。")
        print("=" * 60)
    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())