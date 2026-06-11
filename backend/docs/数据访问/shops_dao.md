# shops_dao.py — 店铺模块数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/shops_dao.py`
> 对应模型：`models/shops.py` → `Shops` / `Menu` / `Ratings`

---

## 概述

`ShopsDAO` 提供店铺模块三张表的完整数据访问：

- **`Shops`** — 店铺表，核心字段仅保留名称，其余属性通过 DictData + DictRel 字典体系管理
- **`Menu`** — 菜单项表，归属店铺
- **`Ratings`** — 评分表，归属店铺

完整店铺信息（标签、封面图）需在 Service 层组合 `DictRelDAO` + `ImageDAO` 获取。

---

## 数据模型预览

### Shops — 店铺表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 店铺唯一标识 |
| name | VARCHAR(100) | 店铺名称（全平台唯一） |
| view_count | INT (default=0) | 总浏览量（冗余字段） |
| favorite_count | INT (default=0) | 收藏数（冗余字段） |
| comment_count | INT (default=0) | 讨论数（冗余字段） |
| average_rating | FLOAT (default=0.0) | 平均评分（冗余字段） |
| aliases | JSON (NULL) | 别名列表，支持多名称搜索 |
| merged_into | FK → Shops (NULL) | 合并后目标店铺 ID |
| is_banned | BOOLEAN (default=False) | 是否被封禁 |
| is_active | BOOLEAN | 软删除标记（继承自 BaseModel） |

### Menu — 菜单项表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 菜单项唯一标识 |
| shop | FK → Shops | 所属店铺 |
| name | VARCHAR(100) | 菜品名称 |
| price | FLOAT (NULL) | 价格 |
| description | TEXT (NULL) | 菜品描述 |
| is_active | BOOLEAN | 软删除标记（继承自 BaseModel） |

### Ratings — 评分表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 评分唯一标识 |
| user | FK → Users | 评分用户 |
| shop | FK → Shops | 被评店铺 |
| score | INT | 评分值（1-5） |
| is_active | BOOLEAN | 软删除标记（继承自 BaseModel） |

---

## 方法概览

### Shops：单条查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(shop_id, include_inactive)` | `include_inactive` 默认 False | `Optional[Shops]` | 按 ID 查询单条店铺 |
| `get_by_name(name)` | `str` | `Optional[Shops]` | 精确匹配名称（用于查重） |

### Shops：搜索列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `search(keyword, category_ids, district_ids, dining_method_ids, min_rating, sort_by, sort_order, page, page_size)` | 全部可选 | `List[Shops]` | 多条件搜索店铺 |
| `count(keyword, category_ids, district_ids, dining_method_ids, min_rating)` | 全部可选 | `int` | 统计搜索条件下的店铺总数 |

### Shops：写操作

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create(name, **kwargs)` | name 必填 | `Shops` | 创建店铺 |
| `update(shop_id, **kwargs)` | shop_id + 字段 | `Optional[Shops]` | 更新店铺信息 |
| `delete(shop_id)` | `int` | `bool` | 软删除店铺 |
| `increment_view_count(shop_id)` | `int` | `None` | 浏览量原子 +1 |
| `sync_favorite_count(shop_id)` | `int` | `None` | 从 Favorites 表重新计算收藏数 |
| `sync_comment_count(shop_id)` | `int` | `None` | 重新计算讨论数（冗余字段） |

### Menu

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_menu_by_id(menu_id)` | `int` | `Optional[Menu]` | 按 ID 查询菜单项 |
| `get_menu_by_shop(shop_id)` | `int` | `List[Menu]` | 某店铺全部菜单项 |
| `create_menu(shop_id, name, price, description)` | price/description 可选 | `Menu` | 创建菜单项 |
| `update_menu(menu_id, **kwargs)` | menu_id + 字段 | `Optional[Menu]` | 更新菜单项 |
| `delete_menu(menu_id)` | `int` | `bool` | 软删除菜单项 |

### Ratings

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_rating(user_id, shop_id)` | — | `Optional[Ratings]` | 查询某用户对某店铺的评分 |
| `get_ratings_by_shop(shop_id)` | `int` | `List[Ratings]` | 某店铺全部评分列表 |
| `create_or_update_rating(user_id, shop_id, score)` | score 必填 1-5 | `Ratings` | 创建或更新评分，自动重算平均分 |
| `get_rating_distribution(shop_id)` | `int` | `dict` | 评分分布统计 |

---

## 方法详述

### Shops：单条查询

---

#### `get_by_id(shop_id, include_inactive)` — 按 ID 查询单条店铺

根据店铺 ID 查询一条店铺记录。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| shop_id | `int` | ✅ | — | 店铺 ID |
| include_inactive | `bool` | ❌ | `False` | 是否包含已软删除的店铺 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[Shops]` | 找到返回 Tortoise 模型实例；未找到返回 `None` |

**使用示例：**

```python
shop = await ShopsDAO.get_by_id(42)
if shop:
    print(shop.name, shop.average_rating)
```

**业务场景：**
- 店铺详情页基础信息查询
- 删除/修改前校验店铺是否存在

---

#### `get_by_name(name)` — 精确匹配名称（用于查重）

根据店铺名称精确查询，使用 `filter().first()` 而非 `get_or_none()`，避免数据库存在多条同名记录时抛出 `MultipleObjectsReturned`。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| name | `str` | ✅ | 店铺名称 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[Shops]` | 找到返回第一条匹配记录；无匹配或已软删除返回 `None` |

**使用示例：**

```python
existing = await ShopsDAO.get_by_name("老王火锅")
if existing:
    raise ValueError("该店铺名称已存在")
```

**业务场景：**
- 创建店铺前查重，确认无同名活跃店铺
- 搜索时通过别名精确匹配

**实现逻辑（概述）：**
使用 `filter(name=name, is_active=True).first()` 查询，即使数据库有多条同名记录也只返回第一条，不会抛异常。

---

### Shops：搜索列表

---

#### `search(keyword, category_ids, district_ids, dining_method_ids, min_rating, sort_by, sort_order, page, page_size)` — 多条件搜索店铺

多条件组合搜索店铺列表，返回 Shops 实例列表，不 JOIN 字典/图片数据。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| keyword | `Optional[str]` | ❌ | `None` | 关键词模糊搜索（搜索 name 字段） |
| category_ids | `Optional[List[int]]` | ❌ | `None` | 品类标签 ID列表（通过 DictRel 多态关联筛选） |
| district_ids | `Optional[List[int]]` | ❌ | `None` | 区域标签 ID 列表 |
| dining_method_ids | `Optional[List[int]]` | ❌ | `None` | 就餐方式标签 ID 列表 |
| min_rating | `Optional[float]` | ❌ | `None` | 最低平均评分筛选 |
| sort_by | `str` | ❌ | `"favorite_count"` | 排序字段 |
| sort_order | `str` | ❌ | `"desc"` | 排序方向，`"desc"` 或 `"asc"` |
| page | `int` | ❌ | `1` | 页码（从 1 开始） |
| page_size | `int` | ❌ | `20` | 每页条数 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `List[Shops]` | 符合条件的店铺列表（分页） |

**使用示例：**

```python
# 搜索关键词
shops = await ShopsDAO.search(keyword="火锅", page=1, page_size=20)

# 按品类和区域筛选
shops = await ShopsDAO.search(
    category_ids=[1, 2],
    district_ids=[3],
    min_rating=4.0,
    sort_by="average_rating",
    sort_order="desc",
)

# 获取完整信息需组合 DictRelDAO + ImageDAO
for s in shops:
    tags = await DictRelDAO.get_entity_dicts("shop", s.id)
    cover = await ImageDAO.get_first_by_entity("shop", s.id)
```

**业务场景：**
- 首页店铺搜索
- 筛选（品类/区域/就餐方式/最低评分）
- 排序（收藏数/评分/浏览量）

**注意事项：**
- **不 JOIN 字典/图片数据**，Service 层需自行组合 `DictRelDAO` / `ImageDAO` 获取完整信息。
- `category_ids`、`district_ids`、`dining_method_ids` 是 DictData 的 ID 列表，通过 DictRel 多态关联筛选。
- 若某个筛选条件无匹配店铺，直接返回空列表。

---

#### `count(keyword, category_ids, district_ids, dining_method_ids, min_rating)` — 统计店铺总数

统计搜索条件下的店铺总数，用法与 `search()`筛选条件一致。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| keyword | `Optional[str]` | ❌ | `None` | 关键词 |
| category_ids | `Optional[List[int]]` | ❌ | `None` | 品类标签 ID 列表 |
| district_ids | `Optional[List[int]]` | ❌ | `None` | 区域标签 ID 列表 |
| dining_method_ids | `Optional[List[int]]` | ❌ | `None` | 就餐方式标签 ID 列表 |
| min_rating | `Optional[float]` | ❌ | `None` | 最低平均评分 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `int` | 符合条件的店铺总数 |

**业务场景：**
- 配合 `search()` 分页，返回总数用于前端分页器
- 搜索结果计数

---

### Shops：写操作

---

#### `create(name, **kwargs)` — 创建店铺

新建一条店铺记录。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| name | `str` | ✅ | 店铺名称（全平台唯一） |
| **kwargs |任意字段 | ❌ | 其他可选字段（aliases、is_banned 等） |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Shops` | 返回新创建的 Tortoise 模型实例 |

**使用示例：**

```python
shop = await ShopsDAO.create(name="老王火锅", aliases=["老王", "老王店"])
```

**业务场景：**
- 管理员创建新店铺

**实现逻辑（概述）：**
调用 `Shops.create()` 插入数据库，返回新实例。

---

#### `update(shop_id, **kwargs)` — 更新店铺信息

更新指定店铺的字段信息。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| shop_id | `int` | ✅ | 店铺 ID |
| **kwargs | 任意字段 | ✅ | 要更新的字段和值 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[Shops]` | 更新成功返回更新后的实例；店铺不存在或已软删除返回 `None` |

**使用示例：**

```python
updated = await ShopsDAO.update(shop_id=42, name="新名称")
if not updated:
    raise ValueError("店铺不存在")
```

**业务场景：**
- 管理员修改店铺名称
- 更新别名等字段

**实现逻辑（概述）：**
查询 `is_active=True` 记录，若存在则逐字段更新后保存。

---

#### `delete(shop_id)` — 软删除店铺

将指定店铺标记为已删除（`is_active=False`）。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| shop_id | `int` | ✅ | 店铺 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `bool` | 删除成功返回 `True`；店铺不存在返回 `False` |

**使用示例：**

```python
ok = await ShopsDAO.delete(shop_id=42)
if not ok:
    raise ValueError("店铺不存在")
```

**业务场景：**
- 管理员删除违规店铺
- 店铺停业下线

**注意事项：**
- 删除店铺时需同步清理该店铺下的图片、标签、点赞等关联记录，参考「重要约定」章节的级联清理要求。

**实现逻辑（概述）：**
查询 `is_active=True` 记录，若存在则置 `is_active=False` 后保存。

---

#### `increment_view_count(shop_id)` — 浏览量原子 +1

对店铺的浏览量做原子 +1 操作，使用 Tortoise ORM 的 `F()` 表达式实现。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| shop_id | `int` | ✅ | 店铺 ID |

**返回：** `None`

**使用示例：**

```python
await ShopsDAO.increment_view_count(shop_id=42)
```

**业务场景：**
- 用户进入店铺详情页时调用

**注意事项：**
- 使用 `F("view_count") + 1` 原子操作，并发安全。
- 与 `ViewHistoryDAO.upsert` 是两个独立模块：前者是店铺级别的浏览量统计，后者是用户可见的浏览历史。

---

#### `sync_favorite_count(shop_id)` — 从 Favorites 表重新计算收藏数

重新计算店铺的收藏数，更新到 `Shops.favorite_count` 冗余字段。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---:|:---|
| shop_id | `int` | ✅ | 店铺 ID |

**返回：** `None`

**使用示例：**

```python
await ShopsDAO.sync_favorite_count(shop_id=42)
```

**业务场景：**
- 用户收藏/取消收藏操作后同步更新冗余字段
- 定时校准冗余数据

---

#### `sync_comment_count(shop_id)` — 重新计算讨论数

重新计算店铺的讨论数（冗余字段），统计范围与 analytics 总互动数一致：`shop_comments + comment_replies + shop_questions + question_answers`。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| shop_id | `int` | ✅ | 店铺 ID |

**返回：** `None`

**使用示例：**

```python
await ShopsDAO.sync_comment_count(shop_id=42)
```

**业务场景：**
- 店铺详情页展示讨论数
- 定时校准冗余数据

**实现逻辑（概述）：**
执行原生 SQL，统计 shop_comments、comment_replies（通过 join shop_comments）、shop_questions、question_answers（通过 join shop_questions）的活跃记录总数。

---

### Menu

---

#### `get_menu_by_id(menu_id)` — 按 ID 查询菜单项

根据菜单项 ID 查询一条菜单记录。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| menu_id | `int` | ✅ | 菜单项 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[Menu]` | 找到返回 Tortoise 模型实例；未找到或已软删除返回 `None` |

**业务场景：**
- 菜单项详情查询

---

#### `get_menu_by_shop(shop_id)` — 某店铺全部菜单项

获取指定店铺下的所有菜单项，按 id 升序返回。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| shop_id | `int` | ✅ | 店铺 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `List[Menu]` | 该店铺下所有菜单项的列表（按 id 升序） |

**使用示例：**

```python
menu_items = await ShopsDAO.get_menu_by_shop(shop_id=42)
for item in menu_items:
    print(item.name, item.price)
```

**业务场景：**
- 店铺详情页菜单列表

---

#### `create_menu(shop_id, name, price, description)` — 创建菜单项

在指定店铺下新建一条菜单项记录。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| shop_id | `int` | ✅ | — | 所属店铺 ID |
| name | `str` | ✅ | — | 菜品名称 |
| price | `Optional[float]` | ❌ | `None` | 价格 |
| description | `Optional[str]` | ❌ | `None` | 菜品描述 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Menu` | 返回新创建的 Tortoise 模型实例 |

**使用示例：**

```python
item = await ShopsDAO.create_menu(
    shop_id=42,
    name="毛肚",
    price=38.0,
    description="新鲜毛肚，涮8 秒即可",
)
```

**业务场景：**
- 商家添加菜单项

---

#### `update_menu(menu_id, **kwargs)` — 更新菜单项

更新指定菜单项的字段信息。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| menu_id | `int` | ✅ | 菜单项 ID |
| **kwargs | 任意字段 | ✅ | 要更新的字段和值 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[Menu]` | 更新成功返回更新后的实例；菜单项不存在或已软删除返回 `None` |

**使用示例：**

```python
updated = await ShopsDAO.update_menu(menu_id=99, price=42.0)
```

**业务场景：**
- 商家修改菜品价格或描述

---

#### `delete_menu(menu_id)` — 软删除菜单项

将指定菜单项标记为已删除（`is_active=False`）。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| menu_id | `int` | ✅ | 菜单项 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `bool` | 删除成功返回 `True`；菜单项不存在返回 `False` |

**使用示例：**

```python
ok = await ShopsDAO.delete_menu(menu_id=99)
```

**业务场景：**
- 商家删除某道菜品

---

### Ratings

---

#### `get_rating(user_id, shop_id)` — 查询某用户对某店铺的评分

查询指定用户对指定店铺的评分记录。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| user_id | `int` | ✅ | 用户 ID |
| shop_id | `int` | ✅ | 店铺 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[Ratings]` | 找到返回评分实例；未评分返回 `None` |

**使用示例：**

```python
rating = await ShopsDAO.get_rating(user_id=1, shop_id=42)
if rating:
    print(f"用户已评 {rating.score} 星")
else:
    print("用户尚未评分")
```

**业务场景：**
- 判断用户是否已评过分（用于展示/隐藏评分按钮）
- 获取用户历史评分值

---

#### `get_ratings_by_shop(shop_id)` — 某店铺全部评分列表

获取指定店铺下所有评分记录。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| shop_id | `int` | ✅ | 店铺 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `List[Ratings]` | 该店铺下所有评分列表 |

**业务场景：**
- 评分详情页（展示所有用户评分）
- `get_rating_distribution` 的数据来源

---

#### `create_or_update_rating(user_id, shop_id, score)` — 创建或更新评分

用户对店铺进行评分，若已评过则更新分数，每次评分后自动重算店铺的平均评分。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| user_id | `int` | ✅ | 用户 ID |
| shop_id | `int` | ✅ | 店铺 ID |
| score | `int` | ✅ | 评分值（1-5） |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Ratings` | 返回新创建或更新后的评分 Tortoise 模型实例 |

**使用示例：**

```python
rating = await ShopsDAO.create_or_update_rating(
    user_id=user.id,
    shop_id=shop.id,
    score=5,
)
print(f"当前评分：{rating.score} 星")
```

**业务场景：**
- 用户发表评分
- 用户修改自己的评分

**实现逻辑（概述）：**
调用 `Ratings.get_or_create()` 尝试获取或创建记录，若已存在则更新 score 并标记为活跃，最后调用 `_recalc_average_rating()` 重算店铺平均分。

**注意事项：**
- **自动重算平均分**：内部调用 `_recalc_average_rating()` 更新 `Shops.average_rating`，Service 层无需额外操作。
- score 范围1-5，业务层需自行校验。

---

#### `get_rating_distribution(shop_id)` — 评分分布统计

统计指定店铺下各星级评分的分布数量。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| shop_id | `int` | ✅ | 店铺 ID |

**返回：**

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `star_1` | `int` | 1 星评分数 |
| `star_2` | `int` | 2 星评分数 |
| `star_3` | `int` | 3 星评分数 |
| `star_4` | `int` | 4 星评分数 |
| `star_5` | `int` | 5 星评分数 |
| `total` | `int` | 评分总数 |

**使用示例：**

```python
dist = await ShopsDAO.get_rating_distribution(shop_id=42)
print(dist)
# {"star_1": 0, "star_2": 3, "star_3": 5, "star_4": 12, "star_5": 8, "total": 28}
```

**业务场景：**
- 店铺详情页评分分布柱状图
- 配合 `get_ratings_by_shop`展示评分列表

---

###内部方法

---

#### `_recalc_average_rating(shop_id)` — 重新计算并更新店铺平均评分

内部方法，重新计算指定店铺的平均评分并更新到 `Shops.average_rating` 字段。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| shop_id | `int` | ✅ | 店铺 ID |

**返回：** `None`

**实现逻辑（概述）：**
查询该店铺下所有活跃评分记录的 score 值，若无评分则 avg=0.0，否则计算平均值并保留一位小数。

---

## 典型用法汇总

```python
from dao import ShopsDAO, DictRelDAO, ImageDAO

# 1. 店铺详情页 — 基础信息
shop = await ShopsDAO.get_by_id(shop_id=42)
tags = await DictRelDAO.get_entity_dicts("shop", shop.id)
cover = await ImageDAO.get_first_by_entity("shop", shop.id)

# 2. 创建店铺（含查重）
existing = await ShopsDAO.get_by_name("老王火锅")
if existing:
    raise ValueError("该店铺名称已存在")
shop = await ShopsDAO.create(name="老王火锅", aliases=["老王"])

# 3. 首页搜索
shops = await ShopsDAO.search(
    keyword="火锅",
    category_ids=[1, 2],
    min_rating=4.0,
    sort_by="favorite_count",
    sort_order="desc",
    page=1,
    page_size=20,
)
total = await ShopsDAO.count(keyword="火锅", category_ids=[1, 2], min_rating=4.0)

# 4. 进入店铺详情页
await ShopsDAO.increment_view_count(shop_id=shop.id)

# 5. 用户评分
rating = await ShopsDAO.create_or_update_rating(
    user_id=user.id,
    shop_id=shop.id,
    score=5,
)
# 平均分和冗余字段自动更新，无需额外操作

# 6. 查看评分分布
dist = await ShopsDAO.get_rating_distribution(shop_id=shop.id)
print(f"总评分：{dist['total']}，平均 {(dist['star_5']*5 + dist['star_4']*4) / dist['total']:.1f} 星")

# 7. 菜单管理
items = await ShopsDAO.get_menu_by_shop(shop_id=shop.id)
item = await ShopsDAO.create_menu(shop_id=shop.id, name="毛肚", price=38.0)
await ShopsDAO.update_menu(menu_id=item.id, price=42.0)
await ShopsDAO.delete_menu(menu_id=item.id)

# 8. 删除店铺（含级联清理）
ok = await ShopsDAO.delete(shop_id=shop.id)
if ok:
    await ImageDAO.clear_entity_images("shop", shop.id)
    await DictRelDAO.clear_entity_dicts("shop", shop.id)
    await ContentLikes.filter(entity_type="shop", entity_id=shop.id).update(is_active=False)
```

---

## 注意事项

1. **`search` 不 JOIN 字典/图片数据**，Service 层需组合 `DictRelDAO` + `ImageDAO` 获取完整信息。
2. **`create_or_update_rating` 内部自动调用 `_recalc_average_rating`**，Service 层无需额外操作。
3. **`increment_view_count` 使用 `F()` 原子操作**，并发安全，与 `ViewHistoryDAO.upsert` 是两个独立模块。
4. **`get_by_name` 使用 `filter().first()` 而非 `get_or_none()`**，避免多条同名记录时抛异常。
5. **`sync_comment_count` 统计范围与 analytics 总互动数一致**，包括 shop_comments、comment_replies、shop_questions、question_answers。
6. **删除店铺时需同步清理**：图片（`ImageDAO.clear_entity_images`）、字典关联（`DictRelDAO.clear_entity_dicts`）、点赞记录等，参考「重要约定」章节。