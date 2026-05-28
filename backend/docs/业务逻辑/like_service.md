# like_service.py — 统一点赞业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/like_service.py`

---

## 概述

LikeService 根据 `entity_type` 将点赞请求分发到对应的 Service（CommentService / QuestionService），Router 层无需判断类型。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `toggle(user_id, entity_type, entity_id)` | | `dict` | ⭐ 切换点赞，返回 `{is_liked, like_count}` |

---

## 支持的 entity_type

| entity_type | 转发到 | 状态 |
|:---|:---|:---:|
| `shop_comment` | `CommentService.toggle_like()` | ✅ 已实现 |
| `comment_reply` | — | ⏸ TODO |
| `shop_question` | `QuestionService.toggle_like()` | ✅ 已实现 |
| `question_answer` | — | ⏸ TODO |

---

## 典型用法

```python
# Router 层：无需判断类型
result = await LikeService.toggle(user.id, "shop_comment", comment_id)
```
