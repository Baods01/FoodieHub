# shop_service.py — 店铺业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/shop_service.py`

---

## 概述

ShopService 提供店铺、菜单、评分的完整操作。创建店铺时同时完成打标签和初始菜单，评分后自动重算平均分。

---

## 方法列表

### Shops

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create(name, dict_data_ids, menu_items)` | | `ShopResponse` | ⭐ 创建+打标签+可选菜单 |
| `get_by_id(shop_id, user_id)` | user_id 可选 | `Optional[ShopResponse]` | ⭐ 详情+浏览量+收藏状态 |
| `search(keyword, category_ids, district_ids, min_rating, sort_by, sort_order, page, page_size, user_id)` | 全部可选 | `dict` | ⭐ 搜索列表+收藏状态 |
| `update(shop_id, name, dict_data_ids, is_active)` | 字段可选 | `Optional[ShopResponse]` | 管理员更新 |
| `ban_shop(shop_id)` | | `bool` | 封禁店铺 |
| `unban_shop(shop_id)` | | `bool` | 解封店铺 |
| `delete(shop_id)` | | `bool` | 软删除 |

### Menu

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_menu(shop_id)` | | `List[MenuItemResponse]` | 菜单列表 |
| `add_menu_item(shop_id, name, price, description)` | | `MenuItemResponse` | 添加菜品 |
| `remove_menu_item(menu_id)` | | `bool` | 删除菜品 |

### Ratings

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `rate(shop_id, user_id, score)` | 1-5 | `dict` | ⭐ 评分 + 自动重算平均分 |
| `get_rating_distribution(shop_id)` | | `dict` | 评分分布统计 |

---

## 典型用法

```python
# 创建店铺
shop = await ShopService.create(
    name="陈记糖水铺",
    dict_data_ids=[cat_id, area_id],
    menu_items=[{"name": "杨枝甘露", "price": 18}],
)

# 店铺详情
detail = await ShopService.get_by_id(shop.id, user_id=current_user.id)

# 搜索
result = await ShopService.search(keyword="糖水", page=1, page_size=20)

# 评分
await ShopService.rate(shop.id, user.id, 5)
```
