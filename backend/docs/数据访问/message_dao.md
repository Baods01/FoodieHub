# message_dao.py — 消息通知数据访问层

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/message_dao.py`
> 对应模型：`models/users.py` → `Messages`

---

## 概述
MessageDAO 负责消息通知表（Messages）的全部数据访问操作。该表用于存储用户间的通知消息以及系统公告，支持未读计数、批量标记为已读、软删除等操作。Service 层调用此 DAO 进行消息的查询、创建、状态变更和删除。

---

## 数据模型预览
### Messages — 消息表
| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | IntField (pk) | 消息唯一标识 |
| recipient_id | IntField (FK) | 接收用户ID，外键 → Users |
| sender_id | IntField (FK, nullable) | 发送方用户ID，系统消息时为空 |
| type | CharField(50) | 消息类型：announcement、reply_comment、reply_answer、like_comment、like_answer 等 |
| title | CharField(100, nullable) | 消息标题 |
| content | TextField | 消息正文内容 |
| related_entity_type | CharField(50, nullable) | 关联实体类型（如 comment、answer），用于跳转 |
| related_entity_id | IntField (nullable) | 关联实体ID，用于跳转 |
| is_read | BooleanField | 是否已读，默认 False |
| is_active | BooleanField | 软删除标记（继承自 BaseModel），默认 True |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

---

## 方法概览
### 查询
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id` | message_id: int | `Optional[Messages]` | 根据 ID 获取单条消息 |
| `list_by_user` | user_id, unread_only, type, page, page_size | `dict` | 用户消息列表，分页，含未读数 |
| `count_by_user` | user_id, type | `int` | 统计用户消息数量 |
| `get_unread_count` | user_id | `int` | 获取用户未读消息数 |

### 状态变更（读操作）
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|:---|
| `mark_read` | message_id: int | `bool` | 标记单条消息为已读 |
| `mark_all_read` | user_id: int | `int` | 标记用户所有未读消息为已读，返回更新数 |

### 写操作
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|:---|
| `create` | recipient_id, sender_id, type, title, content, related_entity_type, related_entity_id | `Messages` | 创建新消息 |
| `send_announcement` | title, content, sender_id | `int` | 发送系统公告给所有活跃用户，返回发送条数 |
| `delete` | message_id: int | `bool` | 软删除单条消息 |
| `clear_by_user` | user_id: int | `int` | 清空用户所有消息，返回清除数 |

---

## 方法详述

### get_by_id — 根据ID获取消息

**描述：** 根据消息 ID 获取单条消息记录，仅返回未被软删除的消息，并预加载发送方和接收方用户信息。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| message_id | int | 是 | — | 消息 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Optional[Messages]` | 消息模型实例，若不存在或已软删除则返回 None |

**使用示例：**
```python
msg = await MessageDAO.get_by_id(message_id=10)
if msg:
    print(f"消息标题: {msg.title}, 接收者: {msg.recipient_id}")
```

**业务场景：**
- 用户点击消息详情时，根据消息 ID 获取完整消息内容
- 消息推送服务在发送后验证消息是否创建成功

**实现逻辑（概述）：**
调用 `Messages.get_or_none(id=message_id, is_active=True)` 查询，使用 `prefetch_related` 预加载 sender 和 recipient 关系以避免 N+1 查询。

---

### list_by_user — 用户消息列表

**描述：** 获取指定用户的消息列表，按时间倒序排列，支持分页、未读筛选和类型筛选。返回结果中包含未读消息总数，方便前端渲染 badge。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | — | 接收用户 ID |
| unread_only | bool | 否 | False | 是否仅返回未读消息 |
| type | Optional[str] | 否 | None | 按消息类型筛选（如 "announcement"） |
| page | int | 否 | 1 | 页码，从 1 开始 |
| page_size | int | 否 | 20 | 每页条数 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `dict` | 包含 items（消息列表）、total（总数）、page、page_size、unread_count（未读数）的字典 |

**使用示例：**
```python
result = await MessageDAO.list_by_user(
    user_id=1,
    unread_only=False,
    type="announcement",
    page=1,
    page_size=10,
)
print(f"总消息数: {result['total']}, 未读数: {result['unread_count']}")
for msg in result["items"]:
    print(f"- {msg.title}")
```

**业务场景：**
- 用户打开消息中心页面时，加载消息列表
- 前端下拉刷新时加载更多历史消息
- 消息中心筛选特定类型（公告/回复/点赞等）

**实现逻辑（概述）：**
构建 `Messages.filter(recipient_id=user_id, is_active=True)` 查询链，依次应用 unread_only 和 type 过滤条件，先查总数再查分页数据，最后单独查询未读总数，三次查询分别执行。

---

### count_by_user — 统计用户消息数量

**描述：** 统计指定用户的消息总数，可选按类型筛选。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | — | 接收用户 ID |
| type | Optional[str] | 否 | None | 按消息类型筛选 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `int` | 消息总数 |

**使用示例：**
```python
total = await MessageDAO.count_by_user(user_id=1)
announcement_count = await MessageDAO.count_by_user(user_id=1, type="announcement")
```

**业务场景：**
- 消息中心页面显示消息总数
- 后台管理统计用户收件箱数据

**实现逻辑（概述）：**
构建过滤条件后调用 Tortoise ORM 的 `.count()` 方法执行计数查询。

---

### get_unread_count — 获取未读消息数

**描述：** 获取指定用户的未读消息数量，用于前端消息入口红点展示。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | — | 接收用户 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `int` | 未读消息数量 |

**使用示例：**
```python
unread_count = await MessageDAO.get_unread_count(user_id=1)
```

**业务场景：**
- 前端导航栏消息入口显示红点数字
- 页面加载时快速获取未读数，无需加载完整列表

**实现逻辑（概述）：**
过滤 `recipient_id=user_id, is_active=True, is_read=False` 条件后调用 `.count()`。

---

### mark_read — 标记单条消息为已读

**描述：** 将指定消息标记为已读。用于用户查看消息时更新阅读状态。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| message_id | int | 是 | — | 消息 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `bool` | 是否成功标记（消息存在且未被软删除返回 True，否则 False） |

**使用示例：**
```python
success = await MessageDAO.mark_read(message_id=10)
```

**业务场景：**
- 用户点击打开某条消息时，标记为已读
- WebSocket 推送消息后，用户点击查看时更新状态

**实现逻辑（概述）：**
先通过 `get_or_none` 获取消息实例，不存在则返回 False；存在则设置 `is_read=True` 后调用 `.save()` 保存。

---

### mark_all_read — 标记全部未读为已读

**描述：** 将指定用户的所有未读消息批量标记为已读，常用于"全部标为已读"功能。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | — | 接收用户 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `int` | 实际更新（标记）的消息数量 |

**使用示例：**
```python
updated_count = await MessageDAO.mark_all_read(user_id=1)
```

**业务场景：**
- 用户点击消息中心的"全部标为已读"按钮
- 管理员推送公告后，引导用户访问并批量标记已读

**实现逻辑（概述）：**
使用 `Messages.filter(...).update(is_read=True)` 批量更新语法，直接执行 SQL UPDATE，返回影响行数。

---

### create — 创建消息

**描述：** 创建一条新消息记录，用于业务层生成各类通知消息。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| recipient_id | int | 是 | — | 接收用户 ID |
| sender_id | Optional[int] | 否 | None | 发送方用户 ID，系统消息时传 None |
| type | str | 是 | — | 消息类型（announcement/reply_comment/reply_answer/like_comment/like_answer） |
| title | str | 是 | — | 消息标题 |
| content | str | 是 | — | 消息正文内容 |
| related_entity_type | Optional[str] | 否 | None | 关联实体类型，用于跳转（如 "comment"） |
| related_entity_id | Optional[int] | 否 | None | 关联实体 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Messages` | 创建的消息模型实例 |

**使用示例：**
```python
msg = await MessageDAO.create(
    recipient_id=2,
    sender_id=1,
    type="reply_comment",
    title="有人回复了你的评论",
    content="用户张三回复了你的评论：这家店味道不错！",
    related_entity_type="comment",
    related_entity_id=100,
)
```

**业务场景：**
- 用户评论被回复时，Router 层调用 MessageService.create_notification 创建通知消息
- 用户提问被回答时，创建回复通知
- 内容被点赞时创建点赞通知

**实现逻辑（概述）：**
调用 `Messages.create(...)` 插入数据库，返回创建的模型实例。

---

### send_announcement — 发送系统公告

**描述：** 向所有活跃用户发送系统公告，逐条创建消息记录，返回发送条数。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| title | str | 是 | — | 公告标题 |
| content | str | 是 | — | 公告正文内容 |
| sender_id | Optional[int] | 否 | None | 发送者用户 ID（通常为系统管理员） |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `int` | 实际发送的消息条数（即当前活跃用户数） |

**使用示例：**
```python
count = await MessageDAO.send_announcement(
    title="系统升级通知",
    content="平台将于6月15日进行系统升级，届时暂停服务2小时。",
    sender_id=1,
)
print(f"公告已发送给 {count} 位用户")
```

**业务场景：**
- 系统管理员发布全站公告
- 平台运营发送重要通知（如活动公告、规则变更）

**实现逻辑（概述）：**
先查询所有 `is_active=True` 的用户 ID 列表（使用 `.only("id")` 仅取 ID 字段以减少数据传输），然后逐条创建消息记录，最后返回发送总数。

---

### delete — 软删除消息

**描述：** 软删除指定消息，将 `is_active` 设为 False。该方法不会真正从数据库删除记录。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| message_id | int | 是 | — | 消息 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `bool` | 是否成功删除（消息存在且未被软删除返回 True，否则 False） |

**使用示例：**
```python
success = await MessageDAO.delete(message_id=10)
```

**业务场景：**
- 用户手动删除某条消息
- 管理员清理垃圾消息

**实现逻辑（概述）：**
通过 `get_or_none` 获取消息实例，设置 `is_active=False` 后保存。

---

### clear_by_user — 清空用户所有消息

**描述：** 将指定用户的所有消息（is_active=True）批量软删除，常用于用户注销账号前的数据清理。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | — | 用户 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `int` | 实际清除的消息数量 |

**使用示例：**
```python
cleared_count = await MessageDAO.clear_by_user(user_id=5)
```

**业务场景：**
- 用户注销账号时，清空其所有消息记录
- 管理员后台执行用户数据清理

**实现逻辑（概述）：**
使用 `Messages.filter(recipient_id=user_id, is_active=True).update(is_active=False)` 批量更新，直接执行 SQL UPDATE，返回影响行数。