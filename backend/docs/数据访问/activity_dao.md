# activity_dao.py — 动态数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/activity_dao.py`

---

## 概述

activity_dao 提供 Activities 表的访问。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(activity_id)` | `int` | `Optional[Activities]` | 按 ID 查询单条动态 |
| `list_by_user(user_id, page, page_size)` | `page`/`page_size` 默认 1/20 | `dict` | ⭐ 用户动态时间线，按时间倒序，含 `select_related('shop')` |
| `create(user_id, type, target_id, target_type, content, shop_id)` | `content`/`shop_id` 可选 | `Activities` | ⭐ 创建一条动态 |
| `delete(activity_id)` | `int` | `bool` | 软删除 |
| `clear_by_user(user_id)` | `int` | `int` | 用户注销时清理，返回删除数量 |

**`list_by_user` 返回格式：**
```python
{
    "items": [Activities, ...],
    "total": 50,
    "page": 1,
    "page_size": 20
}
```

---

## 典型用法

```python
from dao import ActivityDAO

# 用户评完分后
await ActivityDAO.create(
    user_id=user.id, type="rating",
    target_id=shop_id, target_type="shop",
    content="评分了店铺（4星）", shop_id=shop_id,
)
```

---

## 注意事项

1. **`list_by_user` 带 `select_related('shop')`**，可直接访问 `item.shop.name` 用于前端跳转。
2. **动态自动生成由 Service 层在对应操作后显式调用 `create`**（如评论后、评分后），非自动触发。
3. `type` 取值约定：`comment`、`rating`、`favorite`、`question`、`answer`。
