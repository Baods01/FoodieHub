# question_service.py — 问答业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/question_service.py`

---

## 概述

QuestionService 提供问答区的完整操作：一级问题 CRUD、二级回答、点赞同步。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create(shop_id, user_id, title, content)` | content 可选 | `dict` | 提问（标题必填，描述可选） |
| `list_by_shop(shop_id, page, page_size)` | | `dict` | ⭐ 某店铺的问题列表 |
| `list_by_user(user_id, page, page_size)` | | `dict` | 某用户的问题列表 |
| `update(question_id, title, content)` | 字段可选 | `Optional[dict]` | 更新问题 |
| `delete(question_id)` | | `bool` | 删除问题 |
| `create_answer(question_id, user_id, content, reply_to_user_id)` | reply_to 可选 | `dict` | ⭐ 回答问题 |
| `list_answers(question_id)` | | `list` | 某问题的全部回答 |
| `delete_answer(answer_id)` | | `bool` | |
| `toggle_like(user_id, question_id)` | | `dict` | ⭐ 点赞/取消赞 |

---

## 典型用法

```python
# 提问
q = await QuestionService.create(shop_id, user.id, "人均多少？", content="大概消费范围")

# 获取问答列表
questions = await QuestionService.list_by_shop(shop_id)
for q in questions["items"]:
    answers = await QuestionService.list_answers(q.id)
```
