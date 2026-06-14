"""
activity_signals.py — 活动信号机制

★ 核心设计：利用 Tortoise ORM 的 post_save 事件监听器（Signal），
  当指定的 Model 被 INSERT 时自动生成对应的 Activities 记录。
  这是一种"事件驱动"的编程模式，与传统的"在 Service 层末尾主动调用"互补。

为什么用信号（Signal）而不是在 Service 层手动 create Activity？
  1. 解耦：评论/收藏/评分的 Service 方法不需要关心"还要生成一条动态"这件事，
     信号的触发是透明的——创建评论的代码只关注创建评论本身。
  2. 一致性：无论通过哪个入口创建评论（API、管理后台、数据导入），
     只要有 INSERT 操作，信号就会触发，不会被遗漏。

注册方式：
  在 main.py 的 lifespan 中通过 from services import activity_signals 即可激活。
  不需要在路由或 Service 中显式注册。

[教师可能问：信号机制会不会影响主流程的性能？]
  答：post_save 是同步执行的（在当前协程中串行执行），每条动态的写入
  会增加几十毫秒的响应时间。对于写操作（评论/收藏等）来说，这个开销是合理的。
  如果未来性能成为瓶颈，可以将信号处理改为异步消息队列（如 RabbitMQ/Celery）。

注意事项：
  - 每个信号函数都检查 `if not created: return`，仅处理 INSERT 事件，
    UPDATE 事件（如编辑评论）不会重复生成动态。
  - 对于 CommentReplies 和 QuestionAnswers，需要通过父记录获取 shop_id，
    因为二级回复表本身没有 shop_id 字段（通过 comment_id 或 question_id 间接关联）。
"""

from tortoise.signals import post_save
from dao.activity_dao import ActivityDAO
from models.shops import Ratings
from models.users import Favorites
from models.interaction import ShopComments, CommentReplies, ShopQuestions, QuestionAnswers


# =============================================================================
# 信号 1/6：发表评论 → 生成动态
# 触发时机：ShopComments 表 INSERT 完成后
# 调用链路：
#   Router 层 POST /shops/{shop_id}/comments
#     → CommentService.create()
#       → CommentDAO.create()          ← INSERT INTO shop_comments
#         → Tortoise ORM 自动触发 post_save 信号
#           → 本函数执行 → ActivityDAO.create()
# =============================================================================
@post_save(ShopComments)
async def on_shop_comment_created(sender, instance, created, using_db, update_fields):
    # ★ created 参数：True 表示这是 INSERT 操作，False 表示 UPDATE
    # 我们只在首次创建时生成动态，编辑评论不重复生成
    if not created:
        return
    # instance 就是刚刚 INSERT 的 ShopComments 模型实例
    # instance.shop_id 对应 Shops 表的 FK
    await ActivityDAO.create(
        user_id=instance.user_id,
        type="comment",
        target_id=instance.id,
        target_type="shop_comment",
        shop_id=instance.shop_id,
    )


# =============================================================================
# 信号 2/6：回复评论 → 生成动态
# 触发时机：CommentReplies 表 INSERT 完成后
#
# ★ 关键差异：CommentReplies 只有 comment_id，没有 shop_id
# 需要通过 comment_id 反查父评论的 shop_id
# 这就是"通过父记录获取关联信息"的模式
# =============================================================================
@post_save(CommentReplies)
async def on_comment_reply_created(sender, instance, created, using_db, update_fields):
    if not created:
        return
    # 通过 instance.comment 获取父评论（FK 关联）
    # ★ 这里 await instance.comment 会触发一次 SELECT 查询
    #    [教师可能问：这里会不会导致 N+1？]
    #    答：不会，因为这里只处理单条回复，只查询一次父评论。不是循环。
    parent = await instance.comment
    await ActivityDAO.create(
        user_id=instance.user_id,
        type="reply",
        target_id=instance.id,
        target_type="comment_reply",
        shop_id=parent.shop_id if parent else None,
    )


# =============================================================================
# 信号 3/6：评分店铺 → 生成动态
# 触发时机：Ratings 表 INSERT 完成后
# 评分表直接有 shop_id 字段，不需要反查
# =============================================================================
@post_save(Ratings)
async def on_rating_created(sender, instance, created, using_db, update_fields):
    if not created:
        return
    # instance 是 Ratings 模型实例，直接有 shop_id
    await ActivityDAO.create(
        user_id=instance.user_id,
        type="rating",
        target_id=instance.id,
        target_type="rating",
        shop_id=instance.shop_id,
    )


# =============================================================================
# 信号 4/6：收藏店铺 → 生成动态
# 触发时机：Favorites 表 INSERT 完成后
# 收藏表直接有 shop_id 字段
# =============================================================================
@post_save(Favorites)
async def on_favorite_created(sender, instance, created, using_db, update_fields):
    if not created:
        return
    # ★ 注意：收藏的 target_id 记录的是 shop_id 而不是 Favorites.id
    # 因为前端展示动态时，"收藏了店铺 X"需要知道店铺 ID 来跳转
    # 如果记录的是 Favorites.id，前端还需要再查一次收藏对应的店铺
    await ActivityDAO.create(
        user_id=instance.user_id,
        type="favorite",
        target_id=instance.shop_id,
        target_type="favorite",
        shop_id=instance.shop_id,
    )


# =============================================================================
# 信号 5/6：提出问题 → 生成动态
# 触发时机：ShopQuestions 表 INSERT 完成后
# =============================================================================
@post_save(ShopQuestions)
async def on_shop_question_created(sender, instance, created, using_db, update_fields):
    if not created:
        return
    # ShopQuestions 直接有 shop_id 字段
    await ActivityDAO.create(
        user_id=instance.user_id,
        type="question",
        target_id=instance.id,
        target_type="shop_question",
        shop_id=instance.shop_id,
    )


# =============================================================================
# 信号 6/6：回答问题 → 生成动态
# 触发时机：QuestionAnswers 表 INSERT 完成后
#
# 与 CommentReplies 同理：QuestionAnswers 没有 shop_id，
# 需要通过 question_id 反查父问题的 shop_id
# =============================================================================
@post_save(QuestionAnswers)
async def on_question_answer_created(sender, instance, created, using_db, update_fields):
    if not created:
        return
    # 通过 instance.question 获取父问题（FK 关联）
    parent = await instance.question
    await ActivityDAO.create(
        user_id=instance.user_id,
        type="answer",
        target_id=instance.id,
        target_type="question_answer",
        shop_id=parent.shop_id if parent else None,
    )