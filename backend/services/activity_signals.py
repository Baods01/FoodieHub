"""
活动信号机制 — 利用 Tortoise ORM 的 post_save 事件，
在关键模型写入时自动生成 Activities 记录。

注册方式：main.py 的 lifespan 中 import 本文件即可。
"""

from tortoise.signals import post_save
from dao.activity_dao import ActivityDAO
from models.shops import Ratings
from models.users import Favorites
from models.interaction import ShopComments, CommentReplies, ShopQuestions, QuestionAnswers


@post_save(ShopComments)
async def on_shop_comment_created(sender, instance, created, using_db, update_fields):
    if not created:
        return
    await ActivityDAO.create(
        user_id=instance.user_id,
        type="comment",
        target_id=instance.id,
        target_type="shop_comment",
        shop_id=instance.shop_id,
    )


@post_save(CommentReplies)
async def on_comment_reply_created(sender, instance, created, using_db, update_fields):
    if not created:
        return
    # 通过父评论拿到 shop_id
    parent = await instance.comment
    await ActivityDAO.create(
        user_id=instance.user_id,
        type="reply",
        target_id=instance.id,
        target_type="comment_reply",
        shop_id=parent.shop_id if parent else None,
    )


@post_save(Ratings)
async def on_rating_created(sender, instance, created, using_db, update_fields):
    if not created:
        return
    await ActivityDAO.create(
        user_id=instance.user_id,
        type="rating",
        target_id=instance.id,
        target_type="rating",
        shop_id=instance.shop_id,
    )


@post_save(Favorites)
async def on_favorite_created(sender, instance, created, using_db, update_fields):
    if not created:
        return
    await ActivityDAO.create(
        user_id=instance.user_id,
        type="favorite",
        target_id=instance.shop_id,
        target_type="favorite",
        shop_id=instance.shop_id,
    )


@post_save(ShopQuestions)
async def on_shop_question_created(sender, instance, created, using_db, update_fields):
    if not created:
        return
    await ActivityDAO.create(
        user_id=instance.user_id,
        type="question",
        target_id=instance.id,
        target_type="shop_question",
        shop_id=instance.shop_id,
    )


@post_save(QuestionAnswers)
async def on_question_answer_created(sender, instance, created, using_db, update_fields):
    if not created:
        return
    # 通过父问题拿到 shop_id
    parent = await instance.question
    await ActivityDAO.create(
        user_id=instance.user_id,
        type="answer",
        target_id=instance.id,
        target_type="question_answer",
        shop_id=parent.shop_id if parent else None,
    )

