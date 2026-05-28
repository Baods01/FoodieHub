# like_dao.py — 内容点赞数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/like_dao.py`

---

## 概述

like_dao 提供 ContentLikes 表的完整访问。采用多态关联（entity_type + entity_id），覆盖四种互动内容的点赞。

**不处理 `like_count` 的同步**（Service 层根据 toggle 返回的 action 自行调 CommentDAO/QuestionDAO 增减 count）。

---

## 方法列表

### 查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `is_liked(user_id, entity_type, entity_id)` | 用户 + 内容定位 | `bool` | ⭐ 是否已点赞 |
| `get_by_entity(entity_type, entity_id)` | 内容定位 | `List[ContentLikes]` | 某内容的所有点赞记录 |
| `count_by_entity(entity_type, entity_id)` | 同上 | `int` | ⭐ 点赞总数 |
| `get_by_user(user_id, page, page_size)` | 用户 ID | `dict` | 某用户的点赞记录（分页） |

### 写入

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `like(user_id, entity_type, entity_id)` | 同查询 | `{"action": "liked"}` | 执行点赞（幂等） |
| `unlike(user_id, entity_type, entity_id)` | 同查询 | `{"action": "unliked" 或 "none"}` | 取消点赞 |
| `toggle(user_id, entity_type, entity_id)` | 同查询 | `{"action": "liked"\|"unliked", "is_liked": bool}` | ⭐ 一键切换 |

### 级联清理

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `clear_entity_likes(entity_type, entity_id)` | 内容定位 | `int` | 软删除某内容的所有点赞 |

---

## 核心使用模式（toggle + 同步 count）

```python
from dao import LikeDAO, CommentDAO

# 用户点击点赞按钮
r = await LikeDAO.toggle(user_id, "shop_comment", comment_id)

# 根据切换结果同步冗余计数
if r["action"] == "liked":
    await CommentDAO.increment_like_count(comment_id)
else:
    await CommentDAO.decrement_like_count(comment_id)
```

---

## 注意事项

1. **`toggle` 是推荐方法**，`like` 和 `unlike` 仅在业务逻辑需要明确区分"收藏"和"取消"时使用。
2. **幂等性**：连续两次 `like` 不会创建重复记录，已点赞时直接返回 `"liked"`。
3. **`entity_type` 取值**：`"shop_comment"` / `"comment_reply"` / `"shop_question"` / `"question_answer"`。
