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
    await cursor.execute('''
        ALTER TABLE users 
        ADD COLUMN nickname VARCHAR(30) COMMENT '昵称（用户显示名）' AFTER bio,
        ADD COLUMN gender VARCHAR(10) COMMENT '性别：male/female/other' AFTER nickname
    ''')
    await conn.commit()
    cursor.close()
    conn.close()
    print('字段添加成功')

asyncio.run(main())