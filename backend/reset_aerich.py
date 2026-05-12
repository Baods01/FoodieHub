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
    
    # 清空 aerich 表
    conn = Tortoise.get_connection('default')
    await conn.execute_query('DELETE FROM aerich WHERE app="models"')
    
    print('Success - aerich reset')
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())