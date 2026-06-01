# view_history_dao.py — 浏览历史数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/view_history_dao.py`

---

## 概述

view_history_dao 提供 ViewHistory 表的访问。采用 upsert 模式（浏览同一店铺时更新浏览时间而非创建新记录）。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `upsert(user_id, shop_id)` | | `ViewHistory` | ⭐ 浏览店铺时调用（已存在则更新浏览时间） |
| `list_by_user(user_id, page, page_size)` | `page`/`page_size` 默认 1/20 | `dict` | ⭐ 用户浏览历史，含 `select_related('shop')` |
| `delete(view_history_id)` | `int` | `bool` | 删除单条历史记录 |
| `clear_by_user(user_id)` | `int` | `int` | 清空用户全部历史，返回删除数量 |

---

## 典型用法

```python
from dao import ViewHistoryDAO

# 用户浏览店铺（自动 upsert）
await ViewHistoryDAO.upsert(user_id=user.id, shop_id=shop_id)

# 获取用户浏览历史
history = await ViewHistoryDAO.list_by_user(user_id=user.id, page=1, page_size=20)

# 删除单条
await ViewHistoryDAO.delete(history_id)

# 清空全部
await ViewHistoryDAO.clear_by_user(user_id=user.id)
```

---

## 注意事项

1. **`upsert` 行为**：同一用户对同一店铺再次浏览时，更新 `viewed_at` 时间而非创建新记录，保证历史列表不重复。
2. **`list_by_user` 含 `select_related('shop')`**，可直接访问 `item.shop.name`、`item.shop.id` 等店铺信息。
3. **浏览历史用于"最近浏览"功能**，与"浏览量统计"（`shops_dao.increment_view_count`）是两个独立模块。