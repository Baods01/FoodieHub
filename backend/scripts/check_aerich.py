"""检查数据库中 aerich 表的状态并清理"""
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

    # 检查 aerich 表是否存在
    result = await conn.execute_query("SHOW TABLES LIKE 'aerich'")
    if result[1]:
        print("aerich 表存在，正在删除...")
        count_result = await conn.execute_query("SELECT COUNT(*) as cnt FROM aerich")
        print(f"aerich 表中共 {count_result[1][0]['cnt']} 条记录")
        await conn.execute_query("DROP TABLE IF EXISTS aerich")
        print("aerich 表已删除")

        # 检查是否有其他业务表残留
        result2 = await conn.execute_query("SHOW TABLES")
        all_tables = [row[0] if isinstance(row, (list, tuple)) else list(row.values())[0] for row in result2[1]]
        if all_tables:
            print(f"数据库中还有其他业务表: {all_tables}")
        else:
            print("数据库已空")
    else:
        print("aerich 表不存在，数据库干净")

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())