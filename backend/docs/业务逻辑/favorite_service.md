# favorite_service.py — 收藏业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/favorite_service.py`

---

## 概述

FavoriteService 包装 Favorites 表的 toggle 和查询。toggle 逻辑在 Service 层组合 DAO 实现（判断→删除/创建→返回结果）。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `toggle(user_id, shop_id)` | 用户+店铺 | `dict` | ⭐ 切换收藏，返回 `{is_favorited, favorite_count}` |
| `list(user_id, page, page_size)` | 用户 ID | `dict` | 收藏列表，含店铺名 |
| `list_shop_ids(user_id)` | 用户 ID | `list[int]` | 收藏的店铺 ID 列表 |

---

## 典型用法

```python
# 用户点击收藏按钮
result = await FavoriteService.toggle(user.id, shop.id)
# → {"is_favorited": True, "favorite_count": 42}

# 首页判断各店铺收藏状态
fav_ids = await FavoriteService.list_shop_ids(current_user.id)
for shop in shops:
    shop.is_favorited = shop.id in fav_ids
```
