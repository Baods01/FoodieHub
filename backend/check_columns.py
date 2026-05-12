import asyncio
import asyncmy

async def main():
    conn = await asyncmy.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        database='foodie_hub'
    )
    cursor = conn.cursor()
    await cursor.execute('DESCRIBE users')
    columns = await cursor.fetchall()
    print('users 表的字段：')
    for col in columns:
        print(f'  {col}')
    cursor.close()
    conn.close()

asyncio.run(main())