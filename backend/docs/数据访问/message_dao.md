# message_dao.py — 消息通知数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/message_dao.py`

---

## 概述

message_dao 提供 Messages 表的完整访问。覆盖单条消息和系统公告两种场景。

---

## 方法列表

### 查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(message_id)` | id | `Optional[Messages]` | 单条详情（prefetch sender/recipient） |
| `list_by_user(user_id, unread_only, type, page, page_size)` | 全部可选 | `dict` | ⭐ 用户消息列表，含 `unread_count` |
| `count_by_user(user_id, type)` | type 可选 | `int` | 消息总数 |
| `get_unread_count(user_id)` | | `int` | ⭐ 未读数 |

**`list_by_user` 返回格式：**
```python
{"items": [...], "total": 50, "page": 1, "page_size": 20, "unread_count": 3}
```

### 状态变更

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `mark_read(message_id)` | id | `bool` | ⭐ 标记单条已读 |
| `mark_all_read(user_id)` | | `int` | ⭐ 全部已读，返回标记数 |

### 写入

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create(recipient_id, sender_id, type, title, content, related_entity_type, related_entity_id)` | sender/related 可选 | `Messages` | ⭐ 创建一条消息 |
| `send_announcement(title, content, sender_id)` | | `int` | ⭐ 全站公告，逐条发给所有活跃用户 |

### 删除

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `delete(message_id)` | | `bool` | 软删除单条 |
| `clear_by_user(user_id)` | | `int` | 清空用户所有消息 |

---

## 典型用法

```python
from dao import MessageDAO

# 通知用户
await MessageDAO.create(
    recipient_id=user.id, sender_id=current_user.id,
    type="reply_comment",
    title="新回复",
    content=f"{current_user.username} 回复了你的评论",
    related_entity_type="shop_comment",
    related_entity_id=comment_id,
)

# 标记全部已读
await MessageDAO.mark_all_read(user.id)

# 管理后台发公告
await MessageDAO.send_announcement("系统升级通知", "今晚 2-4 点维护", admin_id=1)
```

---

## 注意事项

1. **`send_announcement` 遍历所有活跃用户逐条插入**，当用户量大时会比较慢（课程设计规模无影响）。
2. **`mark_read` 对已读消息再次调用仍返回 True**（幂等）。
3. **`type` 取值约定**：`"reply_comment"`、`"comment_like"`、`"complaint_result"`、`"announcement"`。
