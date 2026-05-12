import asyncio
from tortoise import Tortoise

async def main():
    await Tortoise.init(
        config={
            "connections": {"default": "mysql://root:123456@localhost:3306/foodie_hub"},
            "apps": {
                "models": {
                    "models": ["models", "aerich.models"],
                    "default_connection": "default",
                },
            },
        }
    )
    
    # 删除最近的迁移记录（需要和数据库实际状态一致）
    conn = Tortoise.get_connection('default')
    await conn.execute_query('DELETE FROM aerich WHERE version LIKE "%3_20260512100007%"')
    
    print('Success - aerich record deleted')
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())