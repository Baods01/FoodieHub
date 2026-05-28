# shops_dao.py — 店铺模块数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/shops_dao.py`

---

## 概述

shops_dao 提供 Shops + Menu + Ratings 三张表的完整访问。三表紧密关联（菜单和评分归属店铺），合并在一个 DAO 中。

完整店铺信息（标签、封面图）需在 Service 层组合 DictRelDAO + ImageDAO 获取。

---

## 方法列表

### Shops 查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(shop_id, include_inactive)` | 后者默认 False | `Optional[Shops]` | 按 ID 查 |
| `get_by_name(name)` | 名称 | `Optional[Shops]` | 精确查重 |
| `search(keyword, category_ids, district_ids, min_rating, sort_by, sort_order, page, page_size)` | 全部可选 | `List[Shops]` | ⭐ 多条件搜索 |
| `count(keyword, category_ids, district_ids, min_rating)` | 同上筛选条件 | `int` | 搜索总数 |

**search 不 JOIN 字典/图片数据**，仅返回 Shops 实例列表。需完整信息时 Service 层组合 DictRelDAO + ImageDAO：

```python
from dao import ShopsDAO, DictRelDAO, ImageDAO

shops = await ShopsDAO.search(keyword="火锅")
for s in shops:
    tags = await DictRelDAO.get_entity_dicts("shop", s.id)
    cover = await ImageDAO.get_first_by_entity("shop", s.id)
```

### Shops 写入

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create(name, **kwargs)` | name 必填 | `Shops` | 创建店铺 |
| `update(shop_id, **kwargs)` | id + 字段 | `Optional[Shops]` | 更新 |
| `delete(shop_id)` | id | `bool` | 软删除 |
| `increment_view_count(shop_id)` | id | `None` | ⭐ 浏览量原子 +1 |

### Menu

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_menu_by_id(menu_id)` | id | `Optional[Menu]` | |
| `get_menu_by_shop(shop_id)` | 店铺 ID | `List[Menu]` | 某店铺全部菜单项 |
| `create_menu(shop_id, name, price, description)` | price/description 可选 | `Menu` | |
| `update_menu(menu_id, **kwargs)` | | `Optional[Menu]` | |
| `delete_menu(menu_id)` | | `bool` | |

### Ratings

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_rating(user_id, shop_id)` | 用户+店铺 | `Optional[Ratings]` | 某人某店评分 |
| `get_ratings_by_shop(shop_id)` | | `List[Ratings]` | 某店全部评分 |
| `create_or_update_rating(user_id, shop_id, score)` | 1-5 | `Ratings` | ⭐ 创建/更新评分，**自动重算 average_rating** |
| `get_rating_distribution(shop_id)` | | `dict` | ⭐ 评分分布统计 |

**`get_rating_distribution` 返回格式：**
```python
{"star_1": 0, "star_2": 3, "star_3": 5, "star_4": 12, "star_5": 8, "total": 28}
```

---

## 注意事项

1. **`create_or_update_rating` 内部自动调用 `_recalc_average_rating`**，Service 层无需额外操作。
2. **`search` 的 `category_ids` 和 `district_ids` 是 DictData 的 ID 列表**，通过 DictRel 多态关联筛选店铺。
3. **`increment_view_count` 使用 `F("view_count") + 1` 原子操作**，并发安全。
