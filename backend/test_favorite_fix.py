#!/usr/bin/env python3
"""
收藏功能修复测试脚本
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dao.favorite_dao import FavoriteDAO
from models.users import Users, Favorites
from models.shops import Shops
from tortoise import Tortoise


async def init_db():
    """初始化数据库连接"""
    await Tortoise.init(
        db_url='mysql://root:123456@localhost:3306/foodiehub_test',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()


async def test_favorite_functionality():
    """测试收藏功能"""
    # 初始化数据库
    await init_db()
    
    try:
        # 创建测试用户和店铺（如果不存在）
        user, _ = await Users.get_or_create(
            id=1,
            defaults={
                'username': 'testuser',
                'password': 'testpass',
                'phone': '13800138000',
                'email': 'test@example.com'
            }
        )
        
        shop, _ = await Shops.get_or_create(
            id=1,
            defaults={
                'name': '测试店铺',
                'description': '这是一个测试店铺'
            }
        )
        
        print("开始测试收藏功能...")
        
        # 第一次收藏
        print("1. 第一次收藏店铺...")
        favorite1 = await FavoriteDAO.add_favorite(user.id, shop.id)
        print(f"   收藏成功: favorite_id={favorite1.id}, is_active={favorite1.is_active}")
        
        # 检查是否已收藏
        is_favorited = await FavoriteDAO.is_favorited(user.id, shop.id)
        print(f"   检查收藏状态: {is_favorited}")
        
        # 取消收藏
        print("2. 取消收藏...")
        result = await FavoriteDAO.remove_favorite(user.id, shop.id)
        print(f"   取消收藏结果: {result}")
        
        # 检查是否已取消收藏
        is_favorited = await FavoriteDAO.is_favorited(user.id, shop.id)
        print(f"   检查收藏状态: {is_favorited}")
        
        # 再次收藏（这是之前会出错的操作）
        print("3. 再次收藏店铺（修复的关键测试）...")
        favorite2 = await FavoriteDAO.add_favorite(user.id, shop.id)
        print(f"   再次收藏成功: favorite_id={favorite2.id}, is_active={favorite2.is_active}")
        
        # 验证是同一条记录
        print(f"   验证是否为同一条记录: {favorite1.id == favorite2.id}")
        
        # 检查最终收藏状态
        is_favorited = await FavoriteDAO.is_favorited(user.id, shop.id)
        print(f"   最终收藏状态: {is_favorited}")
        
        print("测试完成!")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(test_favorite_functionality())