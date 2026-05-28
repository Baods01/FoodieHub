# question_dao.py — 问答区数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/question_dao.py`

---

## 概述

question_dao 提供问答区两张表的完整访问：ShopQuestions（一级问题）+ QuestionAnswers（二级回答）。

---

## 方法列表

### ShopQuestions 查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(question_id)` | | `Optional[ShopQuestions]` | prefetch user |
| `list_by_shop(shop_id, page, page_size)` | | `dict` | ⭐ 某店铺的问题列表 |
| `list_by_user(user_id, page, page_size)` | | `dict` | 某用户的问题列表 |
| `count_by_shop(shop_id)` | | `int` | |

### ShopQuestions 写入

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create(shop_id, user_id, title, content)` | content 可选 | `ShopQuestions` | |
| `update(question_id, title, content)` | 字段可选 | `Optional[ShopQuestions]` | |
| `delete(question_id)` | | `bool` | |
| `increment_like_count` / `decrement_like_count` | question_id | `None` | 原子 ±1 |

### QuestionAnswers

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_answer_by_id(answer_id)` | | `Optional[QuestionAnswers]` | prefetch user + reply_to_user |
| `list_by_question(question_id)` | | `List[QuestionAnswers]` | ⭐ 某问题的所有回答（平铺） |
| `create_answer(question_id, user_id, content, reply_to_user_id)` | reply_to 可选 | `QuestionAnswers` | |
| `delete_answer(answer_id)` | | `bool` | |

---

## 典型用法

```python
from dao import QuestionDAO

# 提问
q = await QuestionDAO.create(shop_id, user_id, "人均多少？", content="大概消费范围")

# 获取问答列表
questions = await QuestionDAO.list_by_shop(shop_id)
for q in questions["items"]:
    answers = await QuestionDAO.list_by_question(q.id)
```

---

## 注意事项

1. **`title` 必填（短概括）、`content` 可选（长描述）**，Service 层需确保至少传 title。
2. 与 CommentDAO 一致的扁平回答设计：所有回答按创建时间平铺返回，`reply_to_user_id` 仅用于 @username 前缀。
