"""
=============================================================================
占位文件：Activity 自动生成机制

TODO — 在 DAO 层开发完成后实现此文件。

=============================================================================
设计目标
------------------------------------------------------------------------------
当用户执行评论、评分、收藏、上传店铺等操作时，自动在 Activities 表中生成
对应的一条动态记录，用于用户主页时间线展示。

当前现状（待修复）：
  各个 Service 手工调用 UserActivitiesService.create_X_activity()，
  分散且容易遗漏。

目标方案：
  利用 Tortoise ORM 的 post_save 信号，监听关键模型的写入事件，
  当发生 insert 操作时自动调用 ActivityService.log()。

完整链路：
  Tortoise post_save
      → 本文件中的信号回调
      → ActivityService.log()          （Service 层）
      → ActivityDAO.create()           （DAO 层）
      → Activities 表写入

文件位置说明：
  - models/   = 数据模型定义（表结构、字段、关系、索引）
  - services/ = 业务逻辑
  - 信号是"事件监听 + 路由到 Service"的胶水层，不属于数据模型，
    因此放在 services/ 下。

=============================================================================
使用方法
------------------------------------------------------------------------------
在 main.py 的 lifespan 中引入本文件以注册信号：

    from services import activity_signals  # 注册 post_save 钩子

=============================================================================
需要监听的事件（按优先级排序）
------------------------------------------------------------------------------
1. ShopComments（一级评论被创建）
   → type="comment", target_id=comment.id, target_type="shop_comment",
     shop_id=comment.shop_id, content="评论了店铺"

2. CommentReplies（二级回复被创建）
   → type="reply", target_id=reply.id, target_type="comment_reply",
     shop_id=comment.shop_id, content="回复了评论"

3. Ratings（评分被创建）
   → type="rating", target_id=rating.id, target_type="rating",
     shop_id=rating.shop_id, content="评分了店铺（N星）"

4. Favorites（收藏被创建）
   → type="favorite", target_id=favorite.shop_id, target_type="favorite",
     shop_id=favorite.shop_id, content="收藏了店铺"

5. ShopQuestions（问题被创建）
   → type="question", target_id=question.id, target_type="shop_question",
     shop_id=question.shop_id, content="提问了关于店铺的问题"

6. Shops（新店铺被创建）
   → type="add_shop", target_id=shop.id, target_type="shop",
     shop_id=shop.id, content="上传了新店铺"

=============================================================================
注意事项
------------------------------------------------------------------------------
- post_save 的 created 参数：True = 新增（应生成动态），False = 更新（应忽略）
- Favorites 使用 is_active 实现收藏切换，应仅在 created=True 时生成，
  取消收藏（is_active=False 的 save）不应生成动态
- 所有回调应尽量轻量，避免拖慢主操作的事务提交
- 用户删除内容后，对应的 Activity 记录不删除（保留历史足迹，内容字段保留原文）
"""

# ==================== 以下为具体实现占位 ====================

# from tortoise.signals import post_save
# from models.shops import Ratings, Shops
# from models.users import Favorites
# from models.interaction import ShopComments, CommentReplies, ShopQuestions
# from services.activity_service import ActivityService
#
#
# @post_save(ShopComments)
# async def on_shop_comment_created(sender, instance, created, using_db, update_fields):
#     if not created:
#         return
#     await ActivityService.log(
#         user=instance.user,
#         action_type="comment",
#         target_id=instance.id,
#         target_type="shop_comment",
#         shop_id=instance.shop_id,
#     )
