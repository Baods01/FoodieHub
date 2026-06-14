"""
activity_service.py — 动态业务逻辑

动态（Activities）是什么？
  用户在平台上的每一次"重要操作"都会生成一条动态记录。
  例如：评论了店铺 → 生成 type="comment" 的动态；收藏了店铺 → 生成 type="favorite" 的动态。
  这些动态在用户个人主页的时间线上展示，类似于"社交动态流"的概念。

动态的生成方式（两种互补机制）：
  1. 主动调用（在 Service 层显式调用 ActivityDAO.create）
     适用于路由层手动触发的场景，见 routers/activities.py。

  2. 信号监听（Tortoise ORM 事件驱动）
     在 activity_signals.py 中注册了 @post_save 钩子，当 ShopComments、Favorites、
     Ratings 等模型被创建时自动生成动态。详见 activity_signals.py 的注释。

  两种方式同时存在，是因为有些动态无法通过 post_save 信号覆盖
  （例如"添加店铺"的 action 需要在业务方法末尾主动记录）。

职责：
  - 从 ActivityDAO 获取 Activities 模型实例
  - 提取关联数据（如通过 FK shop 提取 shop_name）
  - 将 Tortoise ORM 模型实例手动序列化为 dict（因为 FastAPI 不能直接序列化 ORM 对象）

调用链路：
  Router（routers/activities.py）
    → ActivityService.list_by_user()
      → ActivityDAO.list_by_user()      ← 在 dao/activity_dao.py 中查询 Activities 表
        → prefetch_related("shop")      ← 关联查询 shops 表，避免 N+1
      → 手动序列化为 dict

[教师可能问：为什么不用 Pydantic schema 自动序列化？]
  答：因为返回的 dict 需要嵌套 shop_name 字段（来源于关联表），而 Activities 模型
  本身只有 shop_id 外键。如果用 Pydantic schema，需要定义嵌套的 ShopBrief schema。
  手动序列化虽然样板代码多，但对于只有一层的嵌套关系来说更直观。
  如果后续动态接口增加更多字段，应该考虑定义 ActivityResponse schema 来统一管理。
"""

from typing import Optional
from dao.activity_dao import ActivityDAO


class ActivityService:
    """动态业务逻辑"""

    @staticmethod
    async def list_by_user(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        获取用户动态列表，附带关联店铺名称。

        参数说明：
          user_id  : 用户 ID，对应 Activities.user_id（FK → Users 表）
          page     : 页码，从 1 开始，默认 1
          page_size: 每页条数，默认 20

        返回格式：
        {
            "items": [
                {
                    "id": int,
                    "user_id": int,
                    "type": str,           # 动态类型：comment / reply / rating / favorite / question / answer
                    "target_id": int,       # 被操作内容的 ID
                    "target_type": str,     # 被操作内容的类型
                    "content": str | None,  # 动态摘要文本
                    "shop_id": int | None,
                    "shop_name": str | None, # ★ 从 prefetch 的 shop 关联提取
                    "created_at": str,       # ISO 格式时间戳
                },
            ],
            "total": int,
            "page": int,
            "page_size": int,
        }

        ★ 执行顺序说明（先分页查询，再手动序列化）：
          1. 调用 ActivityDAO.list_by_user() 执行分页查询
             DAO 内部做了：
             - Activities.filter(user_id=user_id, is_active=True).order_by("-created_at")
             - offset/limit 分页
             - .count() 统计总数
             - .prefetch_related("shop") 预加载 shop 关联（★ 关键：避免 N+1）
          2. 遍历结果列表，逐条手动提取字段构造 dict
          3. 组装分页元数据返回

        [教师可能问：.prefetch_related("shop") 是做什么的？]
          答：Tortoise-ORM 的 prefetch_related 会在查询主表后，
          额外执行一条 SELECT * FROM shops WHERE id IN (?, ?, ...) 将关联数据批量加载到内存。
          如果不这样做，在 for 循环中访问 item.shop.name 会产生 N+1 次查询，
          每次访问 FK 都触发一次数据库查询。prefetch_related 将 N+1 降为 1+1 次查询。

        [教师可能问：为什么这里选择手动序列化 dict 而不是用 Pydantic？]
          答：因为需要从 item.shop 关联中提取 shop.name，而 Tortoise-ORM 的模型实例
          不是 JSON 可序列化的。直接返回 ORM 对象会报 TypeError。
          手动构造 dict 是最直接、最可控的方式。当字段较少时（~7 个字段），
          手动序列化的代码量并不比定义 Pydantic schema 大多少。
        """
        result = await ActivityDAO.list_by_user(user_id, page=page, page_size=page_size)
        items = result["items"]
        serialized = []
        for item in items:
            # ★ 关键：item.shop 是通过 prefetch_related 预加载的外键关联
            # 如果没有 prefetch，这里 item.shop 会触发一次新的 SELECT 查询
            serialized.append({
                "id": item.id,
                "user_id": item.user_id,
                "type": item.type,
                "target_id": item.target_id,
                "target_type": item.target_type,
                "content": item.content,
                "shop_id": item.shop_id,
                "shop_name": item.shop.name if item.shop else None,
                "created_at": item.created_at.isoformat(),
            })
        return {
            "items": serialized,
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
        }