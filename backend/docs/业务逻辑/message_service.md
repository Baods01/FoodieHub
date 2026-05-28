# message_service.py — 消息通知业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/message_service.py`

---

## 概述

MessageService 提供消息通知的完整操作：查询、已读标记、删除、公告广播。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `list(user_id, unread_only, type, page, page_size)` | 全部可选 | `dict` | ⭐ 消息列表（含 unread_count） |
| `get_unread_count(user_id)` | | `int` | 未读数 |
| `mark_read(user_id, message_ids)` | 校验归属 | `int` | 已标记数 |
| `mark_all_read(user_id)` | | `int` | 已标记数 |
| `delete_messages(user_id, message_ids)` | 校验归属 | `int` | 已删除数 |
| `clear(user_id)` | | `int` | 清空数 |
| `send_announcement(title, content, sender_id)` | | `int` | ⭐ 全站公告 |
| `create_notification(recipient_id, sender_id, type, title, content, ...)` | | `None` | ⭐ 发通知 |

---

## 典型用法

```python
# 通知用户
await MessageService.create_notification(
    recipient_id=user.id, sender_id=current_user.id,
    type="reply_comment", title="新回复",
    content=f"{current_user.username} 回复了你的评论",
)

# 标记已读
await MessageService.mark_read(user.id, [msg_id])

# 管理后台发公告
await MessageService.send_announcement("系统维护", "今晚 2-4 点停机", sender_id=admin.id)
```
