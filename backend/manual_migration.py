import asyncio
from config import settings
from tortoise import Tortoise
from tortoise.connection import connections

async def main():
    await Tortoise.init(
        config={
            "connections": {"default": settings.DATABASE_URL},
            "apps": {
                "models": {
                    "models": ["models", "aerich.models"],
                    "default_connection": "default",
                },
            },
        }
    )
    conn = connections.get('default')
    
    # 删除外键约束
    try:
        await conn.execute_script('ALTER TABLE favorites DROP FOREIGN KEY fk_favorite_users_4c63bcf6')
        print("Dropped foreign key fk_favorite_users_4c63bcf6")
    except Exception as e:
        print(f"Error dropping fk_favorite_users_4c63bcf6: {e}")
    
    try:
        await conn.execute_script('ALTER TABLE favorites DROP FOREIGN KEY fk_favorite_shops_9cf912c0')
        print("Dropped foreign key fk_favorite_shops_9cf912c0")
    except Exception as e:
        print(f"Error dropping fk_favorite_shops_9cf912c0: {e}")
    
    # 删除唯一索引
    try:
        await conn.execute_script('ALTER TABLE favorites DROP INDEX uid_favorites_user_id_80cb0d')
        print("Dropped unique index uid_favorites_user_id_80cb0d")
    except Exception as e:
        print(f"Error dropping unique index: {e}")
    
    # 创建新索引
    try:
        await conn.execute_script('CREATE INDEX idx_favorites_user_created ON favorites(user_id, created_at)')
        print("Created index idx_favorites_user_created")
    except Exception as e:
        print(f"Error creating index: {e}")
    
    print('Migration completed!')
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())