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
    
    conn = Tortoise.get_connection('default')
    result = await conn.execute_query('SHOW CREATE TABLE favorites')
    print(result[1][0]['Create Table'])
    
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())