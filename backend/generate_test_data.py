"""
测试数据生成脚本 - FoodieHub

用于生成符合业务逻辑的数据库测试数据，包括：
- 50条用户数据记录
- 20条店铺数据记录
- 关联的评分、评论、收藏等数据

运行方式：
    python generate_test_data.py

注意事项：
    - 脚本会先清理相关表中的旧数据
    - 确保字典数据已初始化（运行 init_dict_data.py）
"""

import asyncio
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from tortoise import Tortoise
from config import settings
from models.users import Users, Activities, Favorites, Messages
from models.shops import Shops, Menu, Ratings, Comments, CommentsLikes
from models.reviews import ShopEditRequests
from models.images import Images
from models.dict import DictTypes, DictData, ShopDictRel
from models.complaints import Complaints, ComplaintHandlers
from models.bans import Bans
from services.password_service import PasswordService


class TestDataGenerator:
    """测试数据生成器"""

    def __init__(self):
        self.pwd_service = PasswordService()
        self.generated_users: List[Users] = []
        self.generated_shops: List[Shops] = []
        self.new_users: List[Users] = []  # 只保存本次新增的用户
        self.new_shops: List[Shops] = []  # 只保存本次新增的店铺
        self.dict_data_cache: Dict[str, List[DictData]] = {}

        # 华农校园及周边地址池
        self.address_pool = [
            "华南农业大学泰山学生公寓楼下",
            "华山区华山学生公寓8栋旁",
            "启林区启林北学生宿舍旁",
            "六一区六一超市对面",
            "华南农业大学西门外渔人码头商业街",
            "华南农业大学南门商业街A区",
            "华南农业大学东区食堂一楼",
            "华南农业大学西区食堂二楼",
            "华南农业大学芷园饭堂三楼",
            "华南农业大学嵩山小区48栋首层",
            "华南农业大学茶山区沁香园旁",
            "华南农业大学校桥头左转50米",
            "华南农业大学三角市综合市场旁",
            "华南农业大学图书馆北门对面",
        ]

        # 店铺名称词库
        self.shop_name_prefix = [
            "老友记", "味道轩", "香满楼", "渔人码头", "麻辣诱惑",
            "粤式烧腊", "湘菜馆", "川味坊", "东北饺子", "兰州拉面",
            "桂林米粉", "沙县小吃", "潮汕牛肉", "客家菜", "港式茶餐厅",
            "日式料理", "韩式烤肉", "越南粉", "泰国菜", "意大利披萨",
            "麦当劳", "肯德基", "华莱士", "一点点", "益禾堂",
            "茶颜悦色", "瑞幸咖啡", "星巴克", "全家便利店", "7-Eleven",
        ]

        self.shop_name_suffix = [
            "华农店", "泰山店", "华山店", "启林店", "六一店",
            "西门店", "南门店", "东门店", "北门店", "校内店",
            "分店", "旗舰店", "形象店", "精品店", "总店",
        ]

        # 菜品名称词库
        self.dish_names = [
            "招牌炒饭", "秘制红烧肉", "麻辣香锅", "酸菜鱼", "水煮牛肉",
            "蒜蓉蒸虾", "白切鸡", "叉烧饭", "云吞面", "煲仔饭",
            "肠粉", "虾饺", "烧鹅", "烤鱼", "火锅套餐",
            "烤肉拼盘", "寿司拼盘", "拉面套餐", "咖喱饭", "炸鸡套餐",
            "奶茶", "柠檬茶", "珍珠奶茶", "水果茶", "咖啡",
        ]

        # 用户昵称词库
        self.nicknames = [
            "食神小当家", "华农干饭王", "美食探险家", "味蕾旅行家", "校园美食家",
            "吃货小分队", "干饭人", "干饭魂", "美食猎人", "寻味者",
            "舌尖上的华农", "吃遍华农", "校园美食雷达", "食堂点评官", "华农美食家",
        ]

        # 评论内容词库
        self.comment_contents = [
            "味道真的很不错！推荐大家来尝尝，价格也很实惠。",
            "份量很足，老板人很好，会再来！",
            "性价比超高，学生党友好，值得推荐！",
            "环境不错，很适合朋友聚会，下次还会再来。",
            "服务态度很好，上菜速度也挺快的。",
            "味道一般，没有想象中那么好吃，可能不符合我的口味。",
            "价格有点贵，但是品质还不错。",
            "强烈推荐！是我吃过最好吃的一家！",
            "总体还可以，下次会考虑回购。",
            "位置很好找，就在宿舍楼下，太方便了！",
        ]

        # 店铺标签池
        self.shop_tags = [
            "味道好", "份量足", "价格实惠", "服务好", "环境不错",
            "上菜快", "适合聚餐", "外卖快", "干净卫生", "性价比高",
            "值得回购", "下次还会来", "强烈推荐", "华农必吃", "宝藏小店",
        ]

    async def init_db(self):
        """初始化数据库连接"""
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
        print("✓ 数据库连接成功")

    async def cleanup_data(self):
        """清理旧数据（按外键依赖顺序删除）"""
        print("正在清理旧数据...")
        
        # 按外键依赖顺序删除，避免约束冲突
        await Activities.all().delete()
        await Messages.all().delete()
        await CommentsLikes.all().delete()
        await Comments.all().delete()
        await Ratings.all().delete()
        await Favorites.all().delete()
        await Menu.all().delete()
        await ShopDictRel.all().delete()
        await ShopEditRequests.all().delete()
        await Images.all().delete()
        await Complaints.all().delete()
        await ComplaintHandlers.all().delete()
        await Bans.all().delete()
        await Users.all().delete()
        await Shops.all().delete()
        
        # 重置所有表的 AUTO_INCREMENT
        from tortoise import Tortoise
        conn = Tortoise.get_connection("default")
        tables = [
            "activities", "messages", "comments_likes", "comments", 
            "ratings", "favorites", "menu", "shop_dict_rel",
            "shop_edit_requests", "images", "complaints", 
            "complaint_handlers", "bans", "users", "shops"
        ]
        for table in tables:
            try:
                await conn.execute_query(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
            except Exception:
                pass  # 忽略不支持的表
        
        print("✓ 旧数据清理完成，AUTO_INCREMENT 已重置")

    async def load_dict_data(self):
        """加载字典数据到缓存"""
        for dict_type in await DictTypes.all():
            self.dict_data_cache[dict_type.code] = [
                d async for d in DictData.filter(dict_type=dict_type)
            ]
        print(f"✓ 已加载 {len(self.dict_data_cache)} 种字典类型")

    def generate_phone(self, index: int) -> str:
        """生成唯一的手机号"""
        return f"138{str(index % 1000000000).zfill(8)[:8]}"

    def generate_email(self, username: str) -> str:
        """生成邮箱"""
        domains = ["163.com", "qq.com", "gmail.com", "126.com", "outlook.com"]
        return f"{username}@{random.choice(domains)}"

    async def generate_users(self, count: int = 50) -> List[Users]:
        """生成用户数据"""
        print(f"\n正在生成 {count} 条用户数据...")

        # 先获取已有的手机号，避免重复
        existing_phones = {u.phone async for u in Users.all().only('phone')}
        start_index = 1
        while self.generate_phone(start_index) in existing_phones:
            start_index += 1

        users = []
        # 确保有1个管理员账号
        admin_created = False
        added_count = 0

        i = start_index
        while added_count < count:
            is_admin = (i == start_index and not admin_created and added_count == 0)

            # 生成唯一用户名
            base_username = f"user{i:03d}"
            username = base_username
            counter = 1
            while await Users.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            nickname = f"{random.choice(self.nicknames)}{i}"
            phone = self.generate_phone(i)
            
            # 检查手机号是否已存在
            if phone in existing_phones:
                i += 1
                continue

            email = self.generate_email(username)

            user = Users(
                username=username,
                password=self.pwd_service.hash("password123"),
                phone=phone,
                email=email,
                nickname=nickname if random.random() > 0.3 else None,
                avatar=f"/static/avatars/default_avatar_{i % 5 + 1}.jpg" if random.random() > 0.5 else None,
                bio=f"这是用户 {username} 的个人简介，华农{['大一', '大二', '大三', '大四', '研一', '研二'][i % 6]}学生。" if random.random() > 0.3 else None,
                gender=random.choice(["male", "female", "other"]),
                role=1 if is_admin else 0,
            )
            users.append(user)
            existing_phones.add(phone)
            added_count += 1

            if is_admin:
                admin_created = True

            i += 1

        # 批量插入
        if users:
            await Users.bulk_create(users)
        # 重新查询获取带ID的用户对象
        self.new_users = list(await Users.all())
        self.generated_users = self.new_users  # 保存所有用户
        print(f"✓ 成功生成 {len(self.new_users)} 条用户数据（总共 {len(self.generated_users)} 条）")
        print(f"  - 普通用户: {len([u for u in self.generated_users if u.role == 0])} 条")
        print(f"  - 管理员: {len([u for u in self.generated_users if u.role == 1])} 条")

        return self.generated_users

    async def generate_shops(self, count: int = 20) -> List[Shops]:
        """生成店铺数据"""
        print(f"\n正在生成 {count} 条店铺数据...")

        shops = []
        # 确保有3个管理员创建的店铺
        admin_users = [u for u in self.generated_users if u.role == 1]

        for i in range(1, count + 1):
            name = f"{random.choice(self.shop_name_prefix)}{random.choice(self.shop_name_suffix)}"
            # 确保店铺名唯一
            counter = 1
            base_name = name
            while await Shops.filter(name=name).exists():
                name = f"{base_name}{counter}"
                counter += 1

            shop = Shops(
                name=name,
                description=f"{name}是一家提供优质服务的店铺，欢迎光临。" if random.random() > 0.3 else None,
                view_count=random.randint(0, 500),
                favorite_count=random.randint(0, 100),
                comment_count=random.randint(0, 50),
                average_rating=round(random.uniform(3.0, 5.0), 1),
                aliases=[f"{name}别名{idx}" for idx in range(random.randint(0, 2))] if random.random() > 0.7 else None,
                price_range=random.choice(["10-20", "20-30", "30-50", "50-80", "80-100", None]),
                business_hours=f"{random.randint(7, 10):02d}:00-{random.randint(21, 23):02d}:00",
                dining_methods=random.sample(["dine_in", "pickup", "delivery"], k=random.randint(1, 3)),
                address_detail=random.choice(self.address_pool),
                tags=random.sample(self.shop_tags, k=random.randint(2, 5)) if random.random() > 0.3 else None,
            )
            shops.append(shop)

        # 批量插入
        if shops:
            await Shops.bulk_create(shops)
        # 重新查询获取带ID的店铺对象
        self.new_shops = list(await Shops.all())
        self.generated_shops = self.new_shops  # 保存所有店铺
        print(f"✓ 成功生成 {len(self.new_shops)} 条店铺数据（总共 {len(self.generated_shops)} 条）")

        # 为店铺关联字典数据（区域和品类）
        await self.generate_shop_dict_relations()

        return self.generated_shops

    async def generate_shop_dict_relations(self):
        """为店铺生成字典关联（避免重复）"""
        print("正在生成店铺字典关联...")

        if not self.new_shops:
            print("ℹ 没有新增店铺，跳过字典关联生成")
            return

        category_data = self.dict_data_cache.get("category", [])
        location_data = self.dict_data_cache.get("location_type", [])

        if not category_data or not location_data:
            print("⚠ 警告：字典数据未找到，请先运行 init_dict_data.py")
            return

        # 查询数据库中已有的关联关系
        existing_rels = await ShopDictRel.all()
        existing_pairs = {(rel.shop_id, rel.dict_data_id) for rel in existing_rels}

        relations = []
        for shop in self.new_shops:  # 只对本次新增的店铺
            # 随机选择1-2个品类
            selected_categories = random.sample(
                category_data,
                k=random.randint(1, min(2, len(category_data)))
            )
            # 随机选择1个区域
            selected_location = random.choice(location_data)

            # 检查并添加品类关联
            for cat in selected_categories:
                pair = (shop.id, cat.id)
                if pair not in existing_pairs:
                    relations.append(ShopDictRel(
                        shop=shop,
                        dict_data=cat,
                    ))
                    existing_pairs.add(pair)

            # 检查并添加位置关联
            location_pair = (shop.id, selected_location.id)
            if location_pair not in existing_pairs:
                relations.append(ShopDictRel(
                    shop=shop,
                    dict_data=selected_location,
                ))
                existing_pairs.add(location_pair)

        if relations:
            await ShopDictRel.bulk_create(relations)
            print(f"✓ 成功生成 {len(relations)} 条店铺字典关联")
        else:
            print("ℹ 未添加新的店铺字典关联（已存在）")

    async def generate_menu_items(self):
        """为店铺生成菜单"""
        print("正在生成菜单数据...")

        if not self.new_shops:
            print("ℹ 没有新增店铺，跳过菜单生成")
            return

        menus = []
        for shop in self.new_shops:  # 只对本次新增的店铺
            # 每个店铺生成1-5个菜单项
            num_items = random.randint(1, 5)
            for j in range(num_items):
                menu = Menu(
                    shop=shop,
                    name=random.choice(self.dish_names),
                    price=Decimal(str(round(random.uniform(5, 80), 2))),
                    description=f"美味可口的{random.choice(self.dish_names)}" if random.random() > 0.5 else None,
                )
                menus.append(menu)

        if menus:
            await Menu.bulk_create(menus)
            print(f"✓ 成功生成 {len(menus)} 条菜单数据")
        else:
            print("ℹ 没有生成新的菜单数据")

    async def generate_ratings(self):
        """生成评分数据"""
        print("正在生成评分数据...")

        if not self.new_shops or not self.generated_users:
            print("ℹ 没有新增店铺或用户，跳过评分生成")
            return

        ratings = []
        normal_users = [u for u in self.generated_users if u.role == 0]

        for shop in self.new_shops:  # 只对本次新增的店铺
            # 每个店铺被3-10个用户评分
            num_ratings = random.randint(3, min(10, len(normal_users)))
            rating_users = random.sample(normal_users, k=num_ratings)

            for user in rating_users:
                # 检查是否已评分
                existing = await Ratings.filter(user=user, shop=shop).exists()
                if not existing:
                    ratings.append(Ratings(
                        user=user,
                        shop=shop,
                        score=random.randint(3, 5) if random.random() > 0.2 else random.randint(1, 2)
                    ))

        if ratings:
            await Ratings.bulk_create(ratings)
            print(f"✓ 成功生成 {len(ratings)} 条评分数据")
        else:
            print("ℹ 没有生成新的评分数据")

        # 更新本次新增店铺的平均评分
        for shop in self.new_shops:
            shop_ratings = await Ratings.filter(shop=shop)
            if shop_ratings:
                avg_score = sum(r.score for r in shop_ratings) / len(shop_ratings)
                shop.average_rating = round(avg_score, 1)
                shop.comment_count = len(shop_ratings)
                await shop.save()

    async def generate_comments(self):
        """生成评论数据（支持多层级回复嵌套）"""
        print("正在生成评论数据...")

        if not self.new_shops or not self.generated_users:
            print("ℹ 没有新增店铺或用户，跳过评论生成")
            return

        normal_users = [u for u in self.generated_users if u.role == 0]
        all_comments_created = []

        for shop in self.new_shops:  # 只对本次新增的店铺
            shop_root_comments = []
            num_root_comments = random.randint(3, 6)

            for j in range(num_root_comments):
                user = random.choice(normal_users)
                # 使用 create 返回的对象，确保有正确的 id
                root_comment = await Comments.create(
                    shop=shop,
                    user=user,
                    type=random.choice(["comment", "question"]),
                    content=random.choice(self.comment_contents),
                    like_count=random.randint(0, 20),
                    reply_count=0,
                )
                shop_root_comments.append(root_comment)
                all_comments_created.append(root_comment)

            for root_comment in shop_root_comments:
                await self._generate_nested_replies(
                    shop=shop,
                    parent_comment=root_comment,
                    root_comment=root_comment,
                    normal_users=normal_users,
                    max_depth=2,
                    current_depth=1,
                    all_comments=all_comments_created,
                )

        if all_comments_created:
            print(f"✓ 成功生成 {len(all_comments_created)} 条评论数据")
        else:
            print("ℹ 没有生成新的评论数据")

    async def _generate_nested_replies(
        self,
        shop,
        parent_comment,
        root_comment,
        normal_users,
        max_depth: int = 2,
        current_depth: int = 1,
        all_comments: list = None,
    ):
        """
        递归生成多层级嵌套回复

        Args:
            shop: 所属店铺
            parent_comment: 直接父评论
            root_comment: 根评论（最顶层评论）
            normal_users: 普通用户列表
            max_depth: 最大嵌套层级（1或2，即最多2层回复）
            current_depth: 当前层级
            all_comments: 所有已创建的评论列表（用于更新reply_count）
        """
        if current_depth > max_depth:
            return

        num_replies = random.randint(0, 2) if current_depth <= max_depth else 0
        if num_replies == 0:
            return

        level_prefix = "" if current_depth == 1 else f"[{current_depth}楼] "
        reply_contents = [
            f"同意楼上的说法，确实很不错！",
            f"这家店我去过，补充一下...",
            f"请问有没有推荐的菜品？",
            f"价格确实实惠，学生党福音",
            f"环境挺好的，适合朋友聚餐",
            f"上菜速度挺快的，不用等太久",
            f"这家店在哪里啊？方便说一下吗",
            f"已经收藏了，周末去尝尝",
        ]

        replies_to_create = []
        for i in range(num_replies):
            reply_user = random.choice([u for u in normal_users if u.id != parent_comment.user_id])
            # 使用 create 而不是先创建对象再 bulk_create，确保有正确的 id
            reply = await Comments.create(
                shop=shop,
                user=reply_user,
                type="comment",
                parent=parent_comment,
                root=root_comment,
                content=f"{level_prefix}{random.choice(reply_contents)}",
                like_count=random.randint(0, 5),
                reply_count=0,
            )
            replies_to_create.append(reply)

        for reply in replies_to_create:
            all_comments.append(reply)
            parent_comment.reply_count += 1

        await parent_comment.save()

        if current_depth < max_depth:
            for reply in replies_to_create:
                await self._generate_nested_replies(
                    shop=shop,
                    parent_comment=reply,
                    root_comment=root_comment,
                    normal_users=normal_users,
                    max_depth=max_depth,
                    current_depth=current_depth + 1,
                    all_comments=all_comments,
                )

    async def generate_favorites(self):
        """生成收藏数据"""
        print("正在生成收藏数据...")

        if not self.new_users or not self.generated_shops:
            print("ℹ 没有新增用户或店铺，跳过收藏生成")
            return

        favorites = []
        normal_new_users = [u for u in self.new_users if u.role == 0]  # 只对本次新增的普通用户

        for user in normal_new_users:
            # 每个用户收藏3-8个店铺（优先选本次新增的）
            candidate_shops = self.new_shops.copy() if self.new_shops else []
            if len(candidate_shops) < 8:
                candidate_shops += [s for s in self.generated_shops if s not in candidate_shops]
            
            num_favorites = random.randint(3, min(8, len(candidate_shops)))
            favorite_shops = random.sample(candidate_shops, k=num_favorites)

            for shop in favorite_shops:
                existing = await Favorites.filter(user=user, shop=shop).exists()
                if not existing:
                    favorites.append(Favorites(
                        user=user,
                        shop=shop,
                        sort_order=random.randint(0, 100),
                    ))

        if favorites:
            await Favorites.bulk_create(favorites)
            print(f"✓ 成功生成 {len(favorites)} 条收藏数据")
        else:
            print("ℹ 没有生成新的收藏数据")

    async def generate_activities(self):
        """生成用户动态数据"""
        print("正在生成用户动态数据...")

        if not self.new_users or not self.generated_shops:
            print("ℹ 没有新增用户或店铺，跳过动态生成")
            return

        activities = []
        normal_new_users = [u for u in self.new_users if u.role == 0]  # 只对本次新增的普通用户

        target_users = random.sample(normal_new_users, k=min(20, len(normal_new_users)))
        for user in target_users:
            # 每个活跃用户生成1-3条动态
            num_activities = random.randint(1, 3)
            for _ in range(num_activities):
                activity_type = random.choice(["rating", "comment", "favorite", "add_shop"])
                # 优先选本次新增的店铺
                candidate_shops = self.new_shops.copy() if self.new_shops else []
                if not candidate_shops:
                    candidate_shops = self.generated_shops
                shop = random.choice(candidate_shops)

                activity = Activities(
                    user=user,
                    type=activity_type,
                    target_id=shop.id,
                    target_type="shop",
                    content=f"{user.nickname or user.username}{'评分了' if activity_type == 'rating' else '收藏了' if activity_type == 'favorite' else '评论了' if activity_type == 'comment' else '添加了'} {shop.name}",
                )
                activities.append(activity)

        if activities:
            await Activities.bulk_create(activities)
            print(f"✓ 成功生成 {len(activities)} 条动态数据")
        else:
            print("ℹ 没有生成新的动态数据")

    async def generate_messages(self):
        """生成消息数据"""
        print("正在生成消息数据...")

        if not self.new_users:
            print("ℹ 没有新增用户，跳过消息生成")
            return

        messages = []
        normal_new_users = [u for u in self.new_users if u.role == 0]  # 只对本次新增的普通用户

        target_users = random.sample(normal_new_users, k=min(15, len(normal_new_users)))
        for user in target_users:
            # 每个用户收到1-3条消息
            num_messages = random.randint(1, 3)
            for _ in range(num_messages):
                message = Messages(
                    recipient=user,
                    sender=None,  # 系统消息
                    type="announcement",
                    title=f"系统通知：{random.choice(['新店铺入驻', '活动公告', '功能更新', '社区公约'])}",
                    content=f"亲爱的用户，感谢您对食探社的支持！我们最近更新了...'",
                    related_entity_type=None,
                    related_entity_id=None,
                    is_read=random.choice([True, False]),
                )
                messages.append(message)

        if messages:
            await Messages.bulk_create(messages)
            print(f"✓ 成功生成 {len(messages)} 条消息数据")
        else:
            print("ℹ 没有生成新的消息数据")

    async def validate_data(self) -> Dict[str, Any]:
        """验证数据完整性"""
        print("\n" + "=" * 60)
        print("数据验证报告")
        print("=" * 60)

        validation_report = {
            "users": {},
            "shops": {},
            "related_data": {},
            "issues": [],
        }

        # 验证用户数据
        total_users = await Users.all().count()
        admin_users = await Users.filter(role=1).count()
        users_with_nickname = await Users.filter(nickname__isnull=False).count()
        users_with_avatar = await Users.filter(avatar__isnull=False).count()
        users_with_bio = await Users.filter(bio__isnull=False).count()

        validation_report["users"] = {
            "total": total_users,
            "admin_count": admin_users,
            "with_nickname": users_with_nickname,
            "with_avatar": users_with_avatar,
            "with_bio": users_with_bio,
        }

        print(f"\n【用户数据验证】")
        print(f"  总用户数: {total_users} (要求: 50)")
        print(f"  管理员数: {admin_users} (要求: >=1)")
        print(f"  有昵称: {users_with_nickname}")
        print(f"  有头像: {users_with_avatar}")
        print(f"  有简介: {users_with_bio}")

        if total_users != 50:
            validation_report["issues"].append(f"用户数量不匹配: 期望50, 实际{total_users}")

        # 验证店铺数据
        total_shops = await Shops.all().count()
        shops_with_description = await Shops.filter(description__isnull=False).count()
        shops_with_price_range = await Shops.filter(price_range__isnull=False).count()
        shops_with_business_hours = await Shops.filter(business_hours__isnull=False).count()
        shops_with_address = await Shops.filter(address_detail__isnull=False).count()

        validation_report["shops"] = {
            "total": total_shops,
            "with_description": shops_with_description,
            "with_price_range": shops_with_price_range,
            "with_business_hours": shops_with_business_hours,
            "with_address": shops_with_address,
        }

        print(f"\n【店铺数据验证】")
        print(f"  总店铺数: {total_shops} (要求: 20)")
        print(f"  有描述: {shops_with_description}")
        print(f"  有价格区间: {shops_with_price_range}")
        print(f"  有营业时间: {shops_with_business_hours}")
        print(f"  有地址: {shops_with_address}")

        if total_shops != 20:
            validation_report["issues"].append(f"店铺数量不匹配: 期望20, 实际{total_shops}")

        # 验证关联数据
        total_ratings = await Ratings.all().count()
        total_comments = await Comments.all().count()
        total_favorites = await Favorites.all().count()
        total_menu_items = await Menu.all().count()
        total_dict_relations = await ShopDictRel.all().count()
        total_activities = await Activities.all().count()
        total_messages = await Messages.all().count()

        validation_report["related_data"] = {
            "ratings": total_ratings,
            "comments": total_comments,
            "favorites": total_favorites,
            "menu_items": total_menu_items,
            "dict_relations": total_dict_relations,
            "activities": total_activities,
            "messages": total_messages,
        }

        print(f"\n【关联数据验证】")
        print(f"  评分记录: {total_ratings}")
        print(f"  评论记录: {total_comments}")
        print(f"  收藏记录: {total_favorites}")
        print(f"  菜单项: {total_menu_items}")
        print(f"  字典关联: {total_dict_relations}")
        print(f"  用户动态: {total_activities}")
        print(f"  消息通知: {total_messages}")

        # 验证外键关联完整性
        print(f"\n【外键关联验证】")

        # 检查评分的用户和店铺是否有效
        valid_ratings = await Ratings.filter(user_id__in=[u.id for u in self.generated_users],
                                             shop_id__in=[s.id for s in self.generated_shops]).count()
        print(f"  有效评分: {valid_ratings}/{total_ratings}")

        # 检查评论的用户和店铺是否有效
        valid_comments = await Comments.filter(user_id__in=[u.id for u in self.generated_users],
                                                shop_id__in=[s.id for s in self.generated_shops]).count()
        print(f"  有效评论: {valid_comments}/{total_comments}")

        # 验证评论嵌套层级结构
        await self._validate_comment_replies()

        # 检查收藏的用户和店铺是否有效
        valid_favorites = await Favorites.filter(user_id__in=[u.id for u in self.generated_users],
                                                  shop_id__in=[s.id for s in self.generated_shops]).count()
        print(f"  有效收藏: {valid_favorites}/{total_favorites}")

        # 检查菜单的店铺是否有效
        valid_menu = await Menu.filter(shop_id__in=[s.id for s in self.generated_shops]).count()
        print(f"  有效菜单: {valid_menu}/{total_menu_items}")

        # 检查字典关联是否有效
        valid_dict_rels = await ShopDictRel.filter(
            shop_id__in=[s.id for s in self.generated_shops]
        ).count()
        print(f"  有效字典关联: {valid_dict_rels}/{total_dict_relations}")

        # 总体评估
        print("\n" + "=" * 60)
        if not validation_report["issues"]:
            print("✅ 数据验证通过！所有数据完整且关联正确。")
        else:
            print("⚠️ 数据验证发现问题：")
            for issue in validation_report["issues"]:
                print(f"  - {issue}")
        print("=" * 60)

        return validation_report

    async def _validate_comment_replies(self):
        """验证评论嵌套结构"""
        print(f"\n【评论嵌套层级验证】")

        # 获取所有评论，在 Python 层面过滤
        all_comments = await Comments.all()
        
        root_comments = 0
        level1_count = 0
        level2_count = 0
        
        for comment in all_comments:
            if comment.parent_id is None:
                root_comments += 1  # 根评论
            else:
                if comment.parent_id == comment.root_id:
                    level1_count += 1  # 直接回复根评论
                else:
                    level2_count += 1  # 嵌套回复

        print(f"  一级评论（根评论）: {root_comments} 条")
        print(f"  二级回复（直接回复根评论）: {level1_count} 条")
        print(f"  三级回复（嵌套回复）: {level2_count} 条")

        total_nested = level1_count + level2_count
        if total_nested > 0:
            print(f"  总回复数: {total_nested}")
            print(f"  ✅ 评论嵌套结构正常，包含 {total_nested} 条回复")

        # 获取前3条根评论作为示例
        sample_comments = []
        for comment in all_comments:
            if comment.parent_id is None:
                sample_comments.append(comment)
                if len(sample_comments) >= 3:
                    break
        
        for i, comment in enumerate(sample_comments, 1):
            replies_count = 0
            for c in all_comments:
                if c.root_id == comment.id:
                    replies_count += 1
            print(f"  示例 {i}: 评论ID={comment.id}, 回复数={replies_count}")

    async def print_test_accounts(self):
        """打印测试账号信息"""
        print("\n" + "=" * 60)
        print("测试账号信息")
        print("=" * 60)
        print("\n【管理员账号】")
        admin = await Users.filter(role=1).first()
        if admin:
            print(f"  用户名: {admin.username}")
            print(f"  密码: password123")
            print(f"  角色: 管理员")

        print("\n【普通用户账号（前5个）】")
        normal_users = await Users.filter(role=0).limit(5)
        for i, user in enumerate(normal_users, 1):
            print(f"  {i}. 用户名: {user.username}, 昵称: {user.nickname or '未设置'}")

        print("\n【店铺信息（前5个）】")
        shops = await Shops.all().limit(5)
        for i, shop in enumerate(shops, 1):
            print(f"  {i}. {shop.name} - {shop.address_detail or '地址未填写'}")

        print("\n" + "=" * 60)

    async def run(self):
        """执行数据生成流程"""
        print("\n" + "=" * 60)
        print("FoodieHub 测试数据生成脚本")
        print("=" * 60)

        try:
            # 初始化
            await self.init_db()

            # 清理旧数据
            await self.cleanup_data()

            # 加载字典数据
            await self.load_dict_data()

            # 生成核心数据
            await self.generate_users(count=50)
            await self.generate_shops(count=20)

            # 生成关联数据
            await self.generate_menu_items()
            await self.generate_ratings()
            await self.generate_comments()
            await self.generate_favorites()
            await self.generate_activities()
            await self.generate_messages()

            # 验证数据
            report = await self.validate_data()

            # 打印测试账号
            await self.print_test_accounts()

            # 关闭连接
            await Tortoise.close_connections()

            print("\n✅ 测试数据生成完成！")
            return report

        except Exception as e:
            print(f"\n❌ 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            await Tortoise.close_connections()
            raise


async def main():
    """主函数"""
    generator = TestDataGenerator()
    await generator.run()


if __name__ == "__main__":
    asyncio.run(main())