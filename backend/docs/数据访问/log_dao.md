# log_dao.py — 统一操作日志数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/log_dao.py`

---

## 概述

log_dao 提供 OperationLog 表的写入与查询。日志只追加不修改，不提供更新和删除接口。
is_active 字段仅用于系统内部维护，不开放给用户/管理员操作。

---

## 方法列表

### 写入

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `log(action, operator, operator_name, target_type, target_id, detail, ip_address, user_agent, session_id)` | 除 action 外均可选 | `OperationLog` | ⭐ 记录一条日志 |

`operator` 接收 Users 模型实例或 None。如果传了实例，`operator_name` 会自动从其 username 提取。

**典型用法：**
```python
from dao import LogDAO

# 记录用户操作
await LogDAO.log(
    action="comment",
    operator=current_user,
    target_type="shop_comment",
    target_id=comment_id,
    detail={"shop_id": 123},
)

# 记录匿名操作（未登录用户浏览）
await LogDAO.log(
    action="view_shop",
    target_type="shop",
    target_id=shop_id,
    session_id=session_id,
)
```

### 查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(id)` | id: int | `Optional[OperationLog]` | 单条详情 |
| `list(action, target_type, target_id, operator_id, start_time, end_time, page, page_size)` | 全部可选 | `dict` | ⭐ 管理后台筛选分页 |
| `get_user_view_logs(user_id, action, page, page_size)` | user_id 必填 | `dict` | 用户某类操作记录（如浏览历史） |

**`list` 和 `get_user_view_logs` 返回格式：**
```python
{"items": [...], "total": 100, "page": 1, "page_size": 20}
```

**典型用法：**
```python
# 管理后台查看所有 ban 操作
result = await LogDAO.list(action="ban_user", page=1, page_size=20)

# 用户浏览历史
history = await LogDAO.get_user_view_logs(user_id=123, action="view_shop")
```

### 统计

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `count_by_action(start_time, end_time)` | 可选 | `List[dict]` | 各操作类型数量统计，按 count 降序 |

**返回格式：**
```python
[
    {"action": "view_shop", "count": 1200},
    {"action": "comment",   "count": 300},
    ...
]
```

---

## 注意事项

1. **日志不可修改、不可删除**（DAO 层不提供 update/delete 方法）。需要清理只应由系统管理员直接操作数据库。
2. **`log` 方法的 `action` 和 `target_type` 是数据库 NOT NULL 字段**，即使匿名操作也需要传 `target_type`（如 `"system"`）。
3. **`list` 的筛选参数全为可选**，不传任何筛选则返回全量日志（按时间倒序）。
