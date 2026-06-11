# comment_dao.py — 评论区数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/comment_dao.py`
> 对应模型：`models/interaction.py` → `ShopComments` / `CommentReplies`

---

## 概述

`CommentDAO` 提供评论区两张表的完整数据访问：

- **`ShopComments`** — 一级评论表，挂在某个店铺下
- **`CommentReplies`** — 二级回复表，挂在某条一级评论下，所有回复平铺不嵌套

---

## 数据模型预览

### ShopComments — 一级评论表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 自增主键 |
| shop | FK → Shops | 所属店铺 |
| user | FK → Users | 评论作者 |
| content | TEXT | 评论内容 |
| like_count | INT (default=0) | 点赞数（冗余字段） |
| reply_count | INT (default=0) | 二级回复数（冗余字段） |
| is_active | BOOLEAN | 软删除标记（继承自 BaseModel） |

### CommentReplies — 二级回复表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 自增主键 |
| comment | FK → ShopComments | 所属一级评论 |
| user | FK → Users | 回复作者 |
| content | TEXT | 回复内容 |
| reply_to_user | FK → Users (NULL) | 被回复用户（仅用于前端显示 @username 前缀） |
| like_count | INT (default=0) | 点赞数（冗余字段） |
| is_active | BOOLEAN | 软删除标记（继承自 BaseModel） |

---

## 方法概览

### ShopComments 查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(comment_id)` | `int` | `Optional[ShopComments]` | 按 ID 查询单条评论，prefetch user |
| `list_by_shop(shop_id, page, page_size)` | `page`/`page_size` 默认 1/20 | `dict` | ⭐ 某店铺的一级评论列表（分页） |
| `list_by_user(user_id, page, page_size)` | `page`/`page_size` 默认 1/20 | `dict` | 某用户发表的评论列表（分页） |
| `count_by_shop(shop_id)` | `int` | `int` | 某店铺的一级评论总数 |

### ShopComments 写操作

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create(shop_id, user_id, content)` | — | `ShopComments` | 创建一条一级评论 |
| `update(comment_id, content)` | — | `Optional[ShopComments]` | 修改评论内容 |
| `delete(comment_id)` | — | `bool` | 软删除评论 |
| `increment_like_count(comment_id)` | `int` | `None` | 原子 +1 点赞数 |
| `decrement_like_count(comment_id)` | `int` | `None` | 原子 -1 点赞数（保正） |

### CommentReplies 查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_reply_by_id(reply_id)` | `int` | `Optional[CommentReplies]` | 按 ID 查询单条回复，prefetch user + reply_to_user |
| `list_by_comment(comment_id)` | `int` | `List[CommentReplies]` | ⭐ 某评论的所有二级回复（平铺，按时间正序） |

### CommentReplies 写操作

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create_reply(comment_id, user_id, content, reply_to_user_id)` | `reply_to_user_id` 可选 | `CommentReplies` | 创建一条二级回复 |
| `delete_reply(reply_id)` | `int` | `bool` | 软删除回复 |
| `increment_reply_count(comment_id)` | `int` | `None` | 原子 +1 回复数（更新一级评论） |
| `decrement_reply_count(comment_id)` | `int` | `None` | 原子 -1 回复数（保正） |
| `increment_reply_like_count(reply_id)` | `int` | `None` | 原子 +1 回复点赞数 |
| `decrement_reply_like_count(reply_id)` | `int` | `None` | 原子 -1 回复点赞数（保正） |

### 级联清理

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `clear_by_shop(shop_id)` | `int` | `int` | 店铺删除时清理所有一级评论 |
| `clear_by_user(user_id)` | `int` | `int` | 用户注销时清理其所有一级评论 |

---

## 方法详述

### ShopComments 查询

---

#### `get_by_id(comment_id)` — 按 ID 查询单条一级评论

根据评论 ID 查询一条一级评论，同时预加载作者 user 信息。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| comment_id | `int` | ✅ | 评论记录的主键 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[ShopComments]` | 找到返回 Tortoise 模型实例；未找到或已软删除返回 `None` |

**使用示例：**

```python
comment = await CommentDAO.get_by_id(42)
if comment:
    print(comment.content)
    print(comment.user.username)  # 已 prefetch，可直接访问
```

**业务场景：**
- 评论详情页查询
- 删除/修改前校验评论是否存在

---

#### `list_by_shop(shop_id, page, page_size)` — 某店铺的一级评论列表（分页）

获取指定店铺下所有一级评论，按时间倒序分页返回。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| shop_id | `int` | ✅ | — | 店铺 ID |
| page | `int` | ❌ | `1` | 页码（从 1 开始） |
| page_size | `int` | ❌ | `20` | 每页条数 |

**返回：**

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `items` | `List[ShopComments]` | 当前页的评论记录列表 |
| `total` | `int` | 符合条件的评论总条数 |
| `page` | `int` | 当前页码 |
| `page_size` | `int` | 每页条数 |

**使用示例：**

```python
result = await CommentDAO.list_by_shop(shop_id=1, page=1, page_size=20)
for comment in result["items"]:
    print(comment.user.username, comment.content)
# total=50, page=1, page_size=20
```

**关联预加载：**
- `user` 字段已通过 `prefetch_related("user")` 预加载，可直接访问 `comment.user.username`。

**业务场景：**
- 店铺详情页评论区列表
- 评论分页加载更多

---

#### `list_by_user(user_id, page, page_size)` — 某用户的评论列表（分页）

获取指定用户发表的所有一级评论，按时间倒序分页返回。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | `int` | ✅ | — | 用户 ID |
| page | `int` | ❌ | `1` | 页码 |
| page_size | `int` | ❌ | `20` | 每页条数 |

**返回：** 同 `list_by_shop`，但 `items` 内为该用户发表的 `ShopComments`。

**关联预加载：**
- `shop` 字段已预加载，可直接访问 `comment.shop.name`。

**业务场景：**
- 用户个人主页「我的评论」列表

---

#### `count_by_shop(shop_id)` — 某店铺的一级评论总数

统计指定店铺下活跃一级评论的总数。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| shop_id | `int` | ✅ | 店铺 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `int` | 活跃一级评论的总数 |

**业务场景：**
- 店铺详情页评论数展示
- Service 层同步更新 Shops.comment_count 冗余字段

---

### ShopComments 写操作

---

#### `create(shop_id, user_id, content)` — 创建一级评论

新建一条一级评论记录。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| shop_id | `int` | ✅ | 所属店铺 ID |
| user_id | `int` | ✅ | 评论作者用户 ID |
| content | `str` | ✅ | 评论正文内容 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `ShopComments` | 返回新创建的 Tortoise 模型实例 |

**使用示例：**

```python
comment = await CommentDAO.create(
    shop_id=shop.id,
    user_id=user.id,
    content="味道不错，下次还来！",
)
```

**业务场景：**
- 用户发表一级评论后，Service 层调用
- 通常同步调用 `ActivityDAO.create()` 生成动态

**实现逻辑（概述）：**
调用 `ShopComments.create()` 插入数据库，返回新实例。

---

#### `update(comment_id, content)` — 修改评论内容

修改指定评论的正文内容。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| comment_id | `int` | ✅ | 评论 ID |
| content | `str` | ✅ | 新的评论正文 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[ShopComments]` | 修改成功返回更新后的实例；评论不存在或已软删除返回 `None` |

**使用示例：**

```python
updated = await CommentDAO.update(comment_id=42, content="修改后的内容")
if not updated:
    raise ValueError("评论不存在")
```

**业务场景：**
- 用户编辑自己发表的评论

**实现逻辑（概述）：**
查询 `is_active=True` 记录，若存在则更新 `content` 字段后保存。

---

#### `delete(comment_id)` — 软删除一级评论

将指定一级评论标记为已删除（`is_active=False`）。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| comment_id | `int` | ✅ | 评论 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `bool` | 删除成功返回 `True`；评论不存在返回 `False` |

**使用示例：**

```python
ok = await CommentDAO.delete(42)
if not ok:
    raise ValueError("评论不存在")
```

**业务场景：**
- 用户主动删除自己的评论
- 管理员删除违规评论
- 通常需同步清理该评论下的图片和点赞记录

**实现逻辑（概述）：**
查询 `is_active=True` 的记录，若存在则置 `is_active=False` 后保存。

---

#### `increment_like_count(comment_id)` / `decrement_like_count(comment_id)` — 点赞数原子增减

对一级评论的点赞数做原子加减操作，使用 Tortoise ORM 的 `F()` 表达式实现。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| comment_id | `int` | ✅ | 评论 ID |

**返回：** `None`

**使用示例：**

```python
# 用户点赞时
await CommentDAO.increment_like_count(comment_id=42)

# 用户取消点赞时
await CommentDAO.decrement_like_count(comment_id=42)
```

**注意事项：**
- `decrement_like_count` 在 `like_count__gt=0` 条件下执行，保证不会变为负数
-属于纯原子操作，不返回任何值，调用方需自行维护前端乐观更新或重新查询

---

### CommentReplies 查询

---

#### `get_reply_by_id(reply_id)` — 按 ID 查询单条二级回复

根据回复 ID 查询一条二级回复，预加载回复者用户和被回复用户信息。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| reply_id | `int` | ✅ | 二级回复 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[CommentReplies]` | 找到返回实例；未找到或已软删除返回 `None` |

**关联预加载：**
- `user` — 回复者用户
- `reply_to_user` — 被回复用户（可为 NULL）

**使用示例：**

```python
reply = await CommentDAO.get_reply_by_id(99)
if reply:
    print(reply.user.username, "回复", reply.reply_to_user.username)
```

---

#### `list_by_comment(comment_id)` — 某评论的所有二级回复（平铺）

获取指定一级评论下的所有二级回复，按时间正序返回，所有回复平铺不嵌套。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| comment_id | `int` | ✅ | 一级评论 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `List[CommentReplies]` | 该评论下所有二级回复的列表（按创建时间升序） |

**关联预加载：**
- `user` — 回复者用户
- `reply_to_user` — 被回复用户（可为 NULL）

**使用示例：**

```python
replies = await CommentDAO.list_by_comment(comment_id=42)
for reply in replies:
    prefix = f"@{reply.reply_to_user.username} " if reply.reply_to_user else ""
    print(f"{reply.user.username}：{prefix}{reply.content}")
```

**业务场景：**
- 店铺详情页评论区，加载某条一级评论的全部二级回复
- 回复按时间正序排列，前端直接遍历渲染

**设计说明：**
二级回复之间无嵌套关系（无 `parent_id`），全部平铺。`reply_to_user` 仅用于前端在内容前加 `@username` 前缀，不作为层级依据。

---

### CommentReplies 写操作

---

#### `create_reply(comment_id, user_id, content, reply_to_user_id)` — 创建二级回复

在指定一级评论下新建一条二级回复。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| comment_id | `int` | ✅ | — | 所属一级评论 ID |
| user_id | `int` | ✅ | — | 回复者用户 ID |
| content | `str` | ✅ | — | 回复正文 |
| reply_to_user_id | `Optional[int]` | ❌ | `None` | 被回复用户的 ID（用于 @username 前缀） |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `CommentReplies` | 返回新创建的 Tortoise 模型实例 |

**使用示例：**

```python
# 用户 A 回复用户 B
reply = await CommentDAO.create_reply(
    comment_id=42,
    user_id=user_a.id,
    content="同意！你吃了啥？",
    reply_to_user_id=user_b.id,  # 可选，传 None 表示直接回复，无 @前缀
)
```

**业务场景：**
- 用户发表二级回复后，通常需同步：
  1. 调用 `CommentDAO.increment_reply_count()` 更新一级评论的 `reply_count`
  2. 调用 `ActivityDAO.create()` 生成动态

---

#### `delete_reply(reply_id)` — 软删除二级回复

将指定二级回复标记为已删除（`is_active=False`）。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---:|:---:|:---|
| reply_id | `int` | ✅ | 二级回复 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `bool` | 删除成功返回 `True`；回复不存在返回 `False` |

**使用示例：**

```python
ok = await CommentDAO.delete_reply(99)
```

**业务场景：**
- 用户主动删除自己的回复
- 管理员删除违规回复
- 通常需同步调用 `CommentDAO.decrement_reply_count()`减少一级评论的 `reply_count`

---

#### `increment_reply_count(comment_id)` / `decrement_reply_count(comment_id)` — 一级评论回复数原子增减

对一级评论的 `reply_count` 冗余字段做原子加减操作。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| comment_id | `int` | ✅ | 一级评论 ID |

**返回：** `None`

**使用示例：**

```python
# 发表回复后
await CommentDAO.create_reply(...)
await CommentDAO.increment_reply_count(comment_id=42)

# 删除回复后
await CommentDAO.delete_reply(reply_id=99)
await CommentDAO.decrement_reply_count(comment_id=42)
```

**注意事项：**
- `decrement_reply_count` 在 `reply_count__gt=0` 条件下执行，保证不会变为负数
- 此方法仅更新一级评论的 `reply_count`，不涉及 `CommentReplies` 表

---

#### `increment_reply_like_count(reply_id)` / `decrement_reply_like_count(reply_id)` — 二级回复点赞数原子增减

对二级回复的点赞数做原子加减操作。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| reply_id | `int` | ✅ | 二级回复 ID |

**返回：** `None`

**使用示例：**

```python
# 用户点赞回复时
await CommentDAO.increment_reply_like_count(reply_id=99)

# 用户取消点赞时
await CommentDAO.decrement_reply_like_count(reply_id=99)
```

---

### 级联清理

---

#### `clear_by_shop(shop_id)` — 店铺删除时清理一级评论

将指定店铺下所有一级评论软删除。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| shop_id | `int` | ✅ | 店铺 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `int` | 被清理的评论记录条数 |

**业务场景：**
- 删除店铺时，Service 层同步调用此方法清理该店铺下的所有一级评论
- 二级回复通过数据库外键级联软删除（或由 `comment_id` 关联查询单独清理）

**实现逻辑（概述）：**
批量执行 `UPDATE ... SET is_active=False WHERE shop_id=X AND is_active=True`，返回受影响行数。

---

#### `clear_by_user(user_id)` — 用户注销时清理一级评论

将指定用户发表的所有一级评论软删除。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| user_id | `int` | ✅ | 用户 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `int` | 被清理的评论记录条数 |

**业务场景：**
- 用户注销账户时，Service 层同步调用此方法清理该用户的评论记录

**实现逻辑（概述）：**
批量执行 `UPDATE ... SET is_active=False WHERE user_id=X AND is_active=True`，返回受影响行数。

---

## 典型用法汇总

```python
from dao import CommentDAO, LikeDAO, ActivityDAO

# 1. 店铺详情页 — 评论列表
result = await CommentDAO.list_by_shop(shop_id=shop.id, page=1, page_size=20)
for comment in result["items"]:
    print(comment.user.username, comment.content)

# 2. 发表一级评论
comment = await CommentDAO.create(
    shop_id=shop.id,
    user_id=user.id,
    content="味道不错，下次还来！",
)
# 同步生成动态
await ActivityDAO.create(
    user_id=user.id, type="comment",
    target_id=comment.id, target_type="shop_comment",
    content=f"评论了店铺「{shop.name}」",
    shop_id=shop.id,
)

# 3. 用户点赞评论（Service 中）
r = await LikeDAO.toggle(user_id, "shop_comment", comment.id)
if r["action"] == "liked":
    await CommentDAO.increment_like_count(comment.id)
else:
    await CommentDAO.decrement_like_count(comment.id)

# 4. 发表二级回复
reply = await CommentDAO.create_reply(
    comment_id=comment.id,
    user_id=user.id,
    content="同感！",
    reply_to_user_id=None,
)
await CommentDAO.increment_reply_count(comment.id)

# 5. 加载某评论的全部回复
replies = await CommentDAO.list_by_comment(comment_id=comment.id)
for r in replies:
    prefix = f"@{r.reply_to_user.username} " if r.reply_to_user else ""
    print(f"{r.user.username}：{prefix}{r.content}")

# 6. 删除评论（含清理）
ok = await CommentDAO.delete(comment_id=42)
if ok:
    await Images.filter(entity_type='shop_comment', entity_id=42).update(is_active=False)
    await ContentLikes.filter(entity_type='shop_comment', entity_id=42).update(is_active=False)

# 7. 用户注销 — 清理全部评论
count = await CommentDAO.clear_by_user(user_id=user.id)
print(f"已清理 {count} 条评论")
```

---

## 注意事项

1. **`list_by_shop` / `list_by_comment` 已预加载关联实体**，可直接访问 `comment.user.username`、`reply.user.username`，无需额外查询。
2. **二级回复为扁平设计**，无 `parent_id` 自引用，所有回复按 `created_at` 升序平铺返回，`reply_to_user` 仅用于前端 `@username` 前缀，不构成层级嵌套。
3. **点赞数/回复数增减均为纯原子操作**，不返回任何值，调用方需自行在前端维护乐观更新或重新查询最新值。
4. **`decrement_*` 系列方法均带 `__gt=0` 条件**，保证冗余计数字段不会变为负数。
5. **删除评论时需同步清理**：该评论关联的 Images（`entity_type='shop_comment'`）和 ContentLikes（`entity_type='shop_comment'`）。
6. **`clear_by_shop` 仅清理一级评论**，`CommentReplies` 的清理依赖外键级联或单独查询清理。