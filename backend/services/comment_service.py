"""
comment_service.py — 评论业务逻辑

评论系统是"食探社"最核心的互动功能之一。
用户可以对店铺发表评论，其他用户可以在评论下进行二级回复，
每条评论和回复都支持点赞。

数据表结构（见 models/interaction.py）：
  ShopComments（一级评论）
    ├── id, shop_id, user_id, content, like_count, reply_count
    └── CommentReplies（二级回复，扁平结构）
        └── id, comment_id, user_id, content, reply_to_user_id, like_count

★ 扁平回复设计：
  所有二级回复直接关联到一级评论（comment_id），不嵌套多层。
  reply_to_user_id 记录"这条回复是在回复谁的"，仅用于前端 @username 前缀显示。
  这种设计避免了无限嵌套的递归查询问题。

图片关联修正策略（★ 答辩重点）：
  用户发表评论时可以附带一张图片。
  前端的操作流程是：
    1. 用户上传图片 → 返回 image_id
    2. 用户提交评论时，将 image_id 传过来
  但上传图片时，前端还不知道评论 ID，所以图片的 entity_id 被临时设为 shop_id。
  评论创建后，需要通过 image_id 反查图片记录，将 entity_id 修正为真正的评论 ID。
  这就是 CommentService.create() 中的"先占位、后修正"逻辑。
"""

from typing import Optional, List
from dao.comment_dao import CommentDAO
from dao.like_dao import LikeDAO
from dao.shops_dao import ShopsDAO


class CommentService:
    """评论业务逻辑"""

    @staticmethod
    async def create(shop_id: int, user_id: int, content: str, image_id: Optional[int] = None) -> dict:
        """
        创建一级评论。

        ★ 完整执行顺序（7 步）：
          1. CommentDAO.create() → INSERT INTO shop_comments
             插入评论记录，此时评论有 id 了
          2. ShopsDAO.sync_comment_count(shop_id) → 同步店铺讨论数
             执行原生 SQL 跨 4 张表重算总数
          3. 如果传了 image_id：
             a. 反查图片记录：ImageDAO.get_by_id(image_id)
             b. 防御性检查：校验 entity_type="shop_comment" 且 entity_id==shop_id
             c. 修正：将 entity_id 从 shop_id 改为真实的评论 id
          4. fetch_related("user") → 加载评论者信息
          5. 如果传了 image_id，重新获取图片 URL（因为 entity_id 刚被修正过）
          6. 手动序列化（嵌套 user 对象和 image URL）

        [教师可能问：为什么要在 Service 层修正图片的 entity_id，而不是直接上传时就传评论 ID？]
          答：因为评论还没创建，前端不可能知道评论 ID。有两种方案：
          方案 A（当前实现）：先上传图片（entity_id=shop_id），创建评论后再修正
          方案 B：先创建评论（返回评论 ID），再上传图片（带上评论 ID）
          方案 A 的好处是前端可以"一次提交"（图片和评论内容一起发），用户体验更好。
          方案 B 需要前端先调一次创建接口，拿到评论 ID 后再调图片上传接口，多了网络往返。
        """
        # 第 1 步：创建评论
        c = await CommentDAO.create(shop_id, user_id, content)

        # 第 2 步：同步店铺讨论数（兜底重算）
        await ShopsDAO.sync_comment_count(shop_id)

        # 第 3 步：图片关联修正（先占位后修正）
        if image_id:
            from dao.image_dao import ImageDAO
            img = await ImageDAO.get_by_id(image_id)
            # ★ 防御性检查：确认图片的类型和占位 ID 正确
            if img and img.entity_type == "shop_comment" and img.entity_id == shop_id:
                await ImageDAO.update(image_id, entity_id=c.id)

        # 第 4 步：加载用户关联
        await c.fetch_related("user")
        user = c.user

        # 第 5 步：重新获取修正后的图片 URL
        image_url = None
        if image_id:
            img = await ImageDAO.get_by_id(image_id)
            if img:
                image_url = img.url

        # 第 6 步：手动序列化
        return {
            "id": c.id,
            "shop_id": c.shop_id,
            "user": {"id": user.id, "username": user.username, "avatar": user.avatar} if user else None,
            "content": c.content,
            "image": image_url,
            "like_count": 0,
            "reply_count": 0,
            "created_at": c.created_at.isoformat(),
        }

    @staticmethod
    async def list_by_shop(shop_id: int, page: int = 1, page_size: int = 20, user_id: Optional[int] = None) -> dict:
        """
        获取店铺的评论列表（分页，含用户点赞状态）。

        ★ 执行顺序：
          1. CommentDAO.list_by_shop() → 分页查询评论
             DAO 内部：.prefetch_related("user").order_by("-created_at").offset().limit()
          2. 对每条评论：
             a. 如果传了 user_id，查该用户是否已点赞（★ N+1）
             b. 查评论图片（★ N+1）
             c. 手动序列化
          3. 返回分页数据

        这里的两个 N+1 问题（has_liked + 图片）是主要性能隐患。
        改进方案参见 ShopService.search 中的批量处理模式。
        """
        result = await CommentDAO.list_by_shop(shop_id, page=page, page_size=page_size)
        from dao.image_dao import ImageDAO
        items = []
        for c in result["items"]:
            user = c.user
            # ★ N+1 风险点 1：每条评论都查一次点赞状态
            has_liked = False
            if user_id is not None:
                has_liked = await LikeDAO.is_liked(user_id, "shop_comment", c.id)
            # ★ N+1 风险点 2：每条评论都查一次图片
            imgs = await ImageDAO.get_by_entity("shop_comment", c.id)
            image_url = imgs[0].url if imgs else None
            items.append({
                "id": c.id,
                "shop_id": c.shop_id,
                "user": {"id": user.id, "username": user.username, "avatar": user.avatar} if user else None,
                "content": c.content,
                "image": image_url,
                "like_count": c.like_count,
                "reply_count": c.reply_count,
                "has_liked": has_liked,
                "created_at": c.created_at.isoformat(),
            })
        return {"items": items, "total": result["total"], "page": result["page"], "page_size": result["page_size"]}

    @staticmethod
    async def list_by_user(user_id: int, page: int = 1, page_size: int = 20) -> dict:
        """获取某用户的评论列表（查看他/她写过哪些评论）。"""
        return await CommentDAO.list_by_user(user_id, page=page, page_size=page_size)

    @staticmethod
    async def update(comment_id: int, content: str) -> Optional[dict]:
        """更新评论内容（不修改图片）。"""
        c = await CommentDAO.update(comment_id, content)
        if not c:
            return None
        return {"id": c.id, "content": c.content}

    @staticmethod
    async def delete(comment_id: int) -> bool:
        """
        软删除评论，同时同步店铺讨论数。

        ★ 注意：软删除评论后，其下的二级回复仍然存在（is_active=True）。
        在 CommentDAO 中没有级联软删除回复的逻辑。
        但在查询时，CommentReplies 会关联到 comment_id，当评论 is_active=False 时，
        前端的评论列表不会显示这条评论，所以回复也"不可见"了。

        [教师可能问：这和"物理删除"有什么区别？]
          答：物理删除的话，CASCADE 会自动删除所有关联的回复。
          但软删除不会——我们需要手动处理级联。
          当前没有级联软删除回复，意味着数据库中还有"孤儿"回复数据。
          虽然不影响功能，但长期来看会积累无效数据。
        """
        c = await CommentDAO.get_by_id(comment_id)
        ok = await CommentDAO.delete(comment_id)
        if ok and c:
            # 删除评论后重算店铺讨论数
            await ShopsDAO.sync_comment_count(c.shop_id)
        return ok

    # =============================================================================
    # 二级回复
    # =============================================================================

    @staticmethod
    async def create_reply(comment_id: int, user_id: int, content: str,
                           reply_to_user_id: Optional[int] = None) -> dict:
        """
        创建二级回复。

        ★ 执行顺序：
          1. 获取父评论所属的店铺 ID（用于后续同步 comment_count）
             通过 CommentDAO.get_or_none 查询 ShopComments 表
          2. 递增父评论的 reply_count（原子 +1）
             说明：reply_count 是 ShopComments 表的冗余字段，
             每次创建回复时原子递增，不需要兜底重算
          3. CommentDAO.create_reply() → INSERT INTO comment_replies
          4. 同步店铺讨论数
          5. fetch_related("user", "reply_to_user") → 加载关联
          6. 手动序列化

        [教师可能问：为什么 reply_count 用递增而 comment_count 用重算？]
          答：reply_count 只需要统计一级评论下的二级回复数量，
          增量更新（+1/-1）在并发下不会丢失，因为操作的是同一条记录。
          而 comment_count 需要跨 4 张表统计，增量更新容易遗漏
          （比如创建评论时 +1，但同步创建回复时两个操作可能加了两次数），
          所以采用"定期兜底重算"策略。
        """
        # 第 1 步：获取父评论所属店铺 ID
        from models.interaction import ShopComments
        comment = await ShopComments.get_or_none(id=comment_id, is_active=True)
        shop_id = comment.shop_id if comment else None

        # 第 2 步：递增父评论的回复数
        await CommentDAO.increment_reply_count(comment_id)

        # 第 3 步：创建回复
        r = await CommentDAO.create_reply(comment_id, user_id, content, reply_to_user_id)

        # 第 4 步：同步店铺讨论数
        if shop_id:
            await ShopsDAO.sync_comment_count(shop_id)

        # 第 5 步：加载关联
        await r.fetch_related("user", "reply_to_user")
        user = r.user
        reply_to = r.reply_to_user

        # 第 6 步：手动序列化
        return {
            "id": r.id,
            "comment_id": r.comment_id,
            "user": {"id": user.id, "username": user.username, "avatar": user.avatar} if user else None,
            "content": r.content,
            "reply_to_user": {"id": reply_to.id, "username": reply_to.username} if reply_to else None,
            "like_count": 0,
            "created_at": r.created_at.isoformat(),
        }

    @staticmethod
    async def list_replies(comment_id: int, user_id: Optional[int] = None) -> list:
        """
        获取某条评论的所有二级回复。

        返回 list（不分页，因为回复通常不多）。
        同样有 N+1 的 has_liked 查询问题。
        """
        result = await CommentDAO.list_by_comment(comment_id)
        items = []
        for r in result:
            user = r.user
            reply_to = r.reply_to_user
            has_liked = False
            if user_id is not None:
                # ★ N+1 风险点
                has_liked = await LikeDAO.is_liked(user_id, "comment_reply", r.id)
            items.append({
                "id": r.id,
                "comment_id": r.comment_id,
                "user": {"id": user.id, "username": user.username, "avatar": user.avatar} if user else None,
                "content": r.content,
                "reply_to_user": {"id": reply_to.id, "username": reply_to.username} if reply_to else None,
                "like_count": r.like_count,
                "has_liked": has_liked,
                "created_at": r.created_at.isoformat(),
            })
        return items

    @staticmethod
    async def delete_reply(reply_id: int) -> bool:
        """
        软删除二级回复。

        与 delete 类似，软删除回复后需要：
        1. 递减父评论的 reply_count
        2. 同步店铺讨论数
        """
        from models.interaction import CommentReplies, ShopComments
        r = await CommentReplies.get_or_none(id=reply_id, is_active=True)
        if not r:
            return False
        # 获取父评论的店铺 ID
        comment = await ShopComments.get_or_none(id=r.comment_id, is_active=True)
        shop_id = comment.shop_id if comment else None
        ok = await CommentDAO.delete_reply(reply_id)
        if ok:
            # 递减父评论的回复计数
            await CommentDAO.decrement_reply_count(r.comment_id)
            if shop_id:
                await ShopsDAO.sync_comment_count(shop_id)
        return ok

    # =============================================================================
    # 点赞相关（被 LikeService 路由调用）
    # =============================================================================

    @staticmethod
    async def toggle_reply_like(user_id: int, reply_id: int) -> dict:
        """
        切换对二级回复的点赞。

        执行顺序与 QuestionService.toggle_answer_like 一致：
        1. LikeDAO.toggle → 切换 ContentLikes
        2. 根据 action 增减 reply_like_count
        3. 重新 COUNT 最新点赞数
        """
        result = await LikeDAO.toggle(user_id, "comment_reply", reply_id)
        if result["action"] == "liked":
            await CommentDAO.increment_reply_like_count(reply_id)
        elif result["action"] == "unliked":
            await CommentDAO.decrement_reply_like_count(reply_id)
        new_count = await LikeDAO.count_by_entity("comment_reply", reply_id)
        return {"is_liked": result["is_liked"], "like_count": new_count}

    @staticmethod
    async def toggle_like(user_id: int, comment_id: int) -> dict:
        """
        切换对一级评论的点赞。

        与 toggle_reply_like 的区别：
        最后一步读取 like_count 时，用的是 CommentDAO.get_by_id 返回的冗余字段，
        而不是 LikeDAO.count_by_entity——与 QuestionService.toggle_like 的做法一致。

        [教师可能问：为什么 toggle_reply_like 用 count_by_entity 而 toggle_like 读取冗余字段？]
          答：这是一个风格不一致的地方。冗余字段应该是最新值（因为 increment/decrement 是原子操作），
          但 count_by_entity 是"兜底重算"，更准确。两种方法都可以用，
          但应该在项目中统一。当前有两套做法混用了：
          - toggle_like：读冗余字段（快，但可能不精确）
          - toggle_reply_like：重算 COUNT（慢，但精确）
        """
        result = await LikeDAO.toggle(user_id, "shop_comment", comment_id)
        if result["action"] == "liked":
            await CommentDAO.increment_like_count(comment_id)
        elif result["action"] == "unliked":
            await CommentDAO.decrement_like_count(comment_id)
        new_count = (await CommentDAO.get_by_id(comment_id)).like_count
        return {"is_liked": result["is_liked"], "like_count": new_count}