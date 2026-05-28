# activity_dao.py — 动态数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/activity_dao.py`

---

## 概述

activity_dao 提供 Activities 表的访问。Activity 的自动生成机制见 `services/activity_signals.py`（占位），DAO 层仅提供基础 CRUD。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(activity_id)` | | `Optional[Activities]` | |
| `list_by_user(user_id, page, page_size)` | | `dict` | ⭐ 用户主页时间线，按时间倒序 |
| `create(user_id, type, target_id, target_type, content, shop_id)` | 后三可选 | `Activities` | ⭐ 创建一条动态 |
| `delete(activity_id)` | | `bool` | 软删除 |
| `clear_by_user(user_id)` | | `int` | 用户注销时清理 |

---

## 典型用法

```python
from dao import ActivityDAO

# 用户评完分后
await ActivityDAO.create(
    user_id=user.id, type="rating",
    target_id=shop_id, target_type="shop",
    content=f"评分了店铺（4星）", shop_id=shop_id,
)
```

---

## 注意事项

1. **`list_by_user` 带 `prefetch_related('shop')`**，可直接访问 `item.shop.name` 用于前端跳转。
2. **动态自动生成尚未实现**，详见 `services/activity_signals.py` 占位文件。
