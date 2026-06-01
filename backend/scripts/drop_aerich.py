"""删除 test1 数据库中的 aerich 表，为全新 init-db 做准备"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise


async def main():
    await Tortoise.init(
        db_url="mysql://root:123456@localhost:3306/test1",
        modules={"models": ["aerich.models"]},
    )
    conn = Tortoise.get_connection("default")
    try:
        await conn.execute_query("DROP TABLE IF EXISTS aerich")
        print("OK: aerich 表已删除")
    except Exception as e:
        print(f"ERROR: {e}")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())