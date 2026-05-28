# comment_dao.py — 评论区数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/comment_dao.py`

---

## 概述

comment_dao 提供评论区两张表的完整访问：ShopComments（一级评论）+ CommentReplies（二级回复）。

---

## 方法列表

### ShopComments 查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(comment_id)` | | `Optional[ShopComments]` | 单条，prefetch user |
| `list_by_shop(shop_id, page, page_size)` | | `dict` | ⭐ 某店铺的一级评论 |
| `list_by_user(user_id, page, page_size)` | | `dict` | 某用户的评论列表 |
| `count_by_shop(shop_id)` | | `int` | |

### ShopComments 写入

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create(shop_id, user_id, content)` | | `ShopComments` | |
| `update(comment_id, content)` | | `Optional[ShopComments]` | |
| `delete(comment_id)` | | `bool` | |
| `increment_like_count` / `decrement_like_count` | comment_id | `None` | 原子 ±1 |
| `increment_reply_count` / `decrement_reply_count` | comment_id | `None` | 原子 ±1 |

### CommentReplies

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_reply_by_id(reply_id)` | | `Optional[CommentReplies]` | prefetch user + reply_to_user |
| `list_by_comment(comment_id)` | | `List[CommentReplies]` | ⭐ 某评论的所有回复（平铺） |
| `create_reply(comment_id, user_id, content, reply_to_user_id)` | reply_to 可选 | `CommentReplies` | |
| `delete_reply(reply_id)` | | `bool` | |

### 级联清理

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `clear_by_shop(shop_id)` | | `int` | 店铺删除时清理 |
| `clear_by_user(user_id)` | | `int` | 用户注销时清理 |

---

## 典型用法

```python
from dao import CommentDAO, LikeDAO

# 发表评论
c = await CommentDAO.create(shop_id, user_id, "好吃！")

# 获取评论列表（含点赞数）
result = await CommentDAO.list_by_shop(shop_id)

# 用户点赞，同步 count
r = await LikeDAO.toggle(user_id, "shop_comment", c.id)
if r["action"] == "liked":
    await CommentDAO.increment_like_count(c.id)
else:
    await CommentDAO.decrement_like_count(c.id)
```

---

## 注意事项

1. **`list_by_shop` / `list_by_comment` prefetch 了 user 信息**，可直接访问 `item.user.username`。
2. **回复的 `reply_to_user` 仅用于 @username 前缀**，不是树形嵌套的依据。所有回复按创建时间平铺返回。
