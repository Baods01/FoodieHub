# favorite_dao.py — 收藏数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/favorite_dao.py`

---

## 概述

favorite_dao 提供 Favorites 表的完整访问。**不处理 toggle 业务逻辑**（Service 层组合 create/remove 实现）。

---

## 方法列表

### 查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(favorite_id)` | id | `Optional[Favorites]` | |
| `is_favorited(user_id, shop_id)` | 用户+店铺 | `bool` | ⭐ 是否已收藏 |
| `list_by_user(user_id, page, page_size)` | 用户 ID | `dict` | ⭐ 收藏列表，附店铺信息 |
| `count_by_user(user_id)` | | `int` | 收藏总数 |
| `count_by_shop(shop_id)` | | `int` | 某店铺被收藏数 |
| `get_shop_ids_by_user(user_id)` | | `List[int]` | ⭐ 用户收藏的店铺 ID 列表 |

### 写入

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create(user_id, shop_id, sort_order)` | sort_order 默认 0 | `Favorites` | 纯插入 |
| `remove(user_id, shop_id)` | 用户+店铺 | `bool` | ⭐ 软删除激活的收藏 |
| `update_sort_order(favorite_id, sort_order)` | | `bool` | 更新排序序号 |

---

## 典型用法（toggle 模式）

```python
from dao import FavoriteDAO

# Service 层的 toggle 逻辑
is_fav = await FavoriteDAO.is_favorited(user_id, shop_id)
if is_fav:
    await FavoriteDAO.remove(user_id, shop_id)
else:
    await FavoriteDAO.create(user_id, shop_id)
```

---

## 注意事项

1. **`create` 不查重、不做 toggle**。调用方需确保逻辑正确（如先调 `is_favorited` 判断）。
2. **`list_by_user` 返回的 items 含 `select_related('shop')`**，可直接访问 `item.shop.name`、`item.shop.id` 等店铺信息。
3. **`remove` 是物理软删除**（`is_active=False`），不会物理摧毁记录，可恢复。
