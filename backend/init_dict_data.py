"""
字典数据初始化脚本

初始化品类和区域字典数据，供店铺创建时使用。

运行方式：
    python -m init_dict_data
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from tortoise import Tortoise
from config import settings
from models.dict import DictTypes, DictData


# 品类字典数据
CATEGORY_DATA = [
    {"code": "local_cuisine", "name": "地方菜"},
    {"code": "hotpot", "name": "火锅"},
    {"code": "barbecue", "name": "烧烤/烤肉"},
    {"code": "western_food", "name": "异域料理"},
    {"code": "snacks", "name": "小吃快餐"},
    {"code": "specialty", "name": "特色菜"},
    {"code": "drinks", "name": "饮品"},
    {"code": "desserts", "name": "甜点/面包"},
]

# 区域字典数据
LOCATION_DATA = [
    # 校内
    {"code": "nei_taisan", "name": "泰山区"},
    {"code": "nei_huashan", "name": "华山区"},
    {"code": "nei_qilin", "name": "启林区"},
    {"code": "nei_liuyi", "name": "六一区"},
    {"code": "zhuxiaoqu", "name": "主校区"},
    # 校外
    {"code": "wai_outside", "name": "校外"},
]


async def init_dict_data():
    """初始化字典数据"""
    # 初始化数据库连接
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
    await Tortoise.generate_schemas(safe=True)

    print("开始初始化字典数据...")

    # 创建品类类型
    category_type, category_created = await DictTypes.get_or_create(
        code="category",
        defaults={
            "name": "店铺品类",
            "target_table": "shops",
            "description": "店铺分类类型，如地方菜、火锅等",
        },
    )
    print(f"{'创建' if category_created else '已存在'} 品类类型: {category_type.name}")

    # 创建区域类型
    location_type, location_created = await DictTypes.get_or_create(
        code="location_type",
        defaults={
            "name": "区域类型",
            "target_table": "shops",
            "description": "店铺所在区域类型，如泰山区、校外等",
        },
    )
    print(f"{'创建' if location_created else '已存在'} 区域类型: {location_type.name}")

    # 初始化品类数据
    for item in CATEGORY_DATA:
        data, created = await DictData.get_or_create(
            dict_type=category_type,
            code=item["code"],
            defaults={
                "name": item["name"],
                "sort_order": len([x for x in CATEGORY_DATA if CATEGORY_DATA.index(x) < CATEGORY_DATA.index(item)]),
            },
        )
        if created:
            print(f"  创建品类: {data.name}")

    # 初始化区域数据
    for item in LOCATION_DATA:
        data, created = await DictData.get_or_create(
            dict_type=location_type,
            code=item["code"],
            defaults={
                "name": item["name"],
                "sort_order": len([x for x in LOCATION_DATA if LOCATION_DATA.index(x) < LOCATION_DATA.index(item)]),
            },
        )
        if created:
            print(f"  创建区域: {data.name}")

    print("\n字典数据初始化完成！")
    print("\n可用的字典数据 ID：")
    print("品类：")
    async for data in DictData.filter(dict_type=category_type):
        print(f"  ID: {data.id} - {data.name} (code: {data.code})")
    print("\n区域：")
    async for data in DictData.filter(dict_type=location_type):
        print(f"  ID: {data.id} - {data.name} (code: {data.code})")

    # 关闭数据库连接
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(init_dict_data())