# analytics_dao.py — 统计分析数据访问

> 面向：业务逻辑层（Service）开发人员、管理后台开发人员
> 文件位置：`dao/analytics_dao.py`
> 对应模型：`models/shops.py` → `Shops`，`models/governance.py` → `Feedback`

---

## 概述

`AnalyticsDAO` 提供管理后台所需的聚合统计数据。复杂聚合使用 raw SQL，展示了 MySQL 8+ 的高级语法（WITH RECURSIVE CTE、标量子查询等）。所有方法均不包含业务语义（不出现"品类""区域"等词汇），字典参数由上游 Service 层传入。

---

## 方法概览

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_overview()` | — | `dict` | 平台概览卡片数据（多表计数） |
| `get_daily_trends(days)` | `days` 默认 `7`，最大 `30` | `list[dict]` | 近 N 天每日新增趋势（CTE + 多表 LEFT JOIN） |
| `count_shops_by_dict_data(dict_data_ids)` | `list[int]` | `list[dict]` | 按字典标签统计各标签关联的店铺数 |
| `get_top_rated_shops(limit)` | `limit` 默认 `10` | `list[dict]` | 评分最高的店铺 TOP N |
| `get_most_favorited_shops(limit)` | `limit` 默认 `10` | `list[dict]` | 收藏最多的店铺 TOP N |
| `get_pending_counts()` | — | `dict` | 各状态待处理的工单数量 |

---

## 方法详述

### `get_overview()` — 平台概览卡片数据

一次性返回管理后台首页所需的全部计数指标，通过一条包含多个标量子查询的 SQL 完成。

**参数：** 无

**返回：**

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `total_shops` | `int` | 活跃且未封禁的店铺总数 |
| `total_users` | `int` | 活跃用户总数 |
| `total_comments` | `int` | 活跃的一级评论 + 二级回复 + 问题 + 回答总数 |
| `total_questions` | `int` | 活跃问题总数 |
| `pending_complaints` | `int` | 状态为 `pending` 且类型为 `complaint` 的反馈工单数 |
| `pending_edits` | `int` | 状态为 `pending` 且类型为 `edit_request` 的反馈工单数 |
| `avg_rating` | `float` | 所有已评分店铺的平均评分（保留一位小数） |

**返回示例：**

```python
{
    "total_shops": 128,
    "total_users": 3450,
    "total_comments": 8720,
    "total_questions": 234,
    "pending_complaints": 3,
    "pending_edits": 1,
    "avg_rating": 4.2,
}
```

**业务场景：**
- 管理后台首页概览卡片，一屏展示平台核心运营指标

**实现逻辑（概述）：**
通过 Tortoise ORM 的 `conn.execute_query()` 执行原生 SQL，内部使用多个标量子查询同时统计各表计数，`avg_rating` 仅统计 `average_rating > 0` 的店铺。

---

### `get_daily_trends(days)` —每日新增趋势

返回近 N 天的每日新增数据（店铺、用户、互动数、问题数），通过 MySQL 8+ 的 `WITH RECURSIVE CTE` 生成日期序列，再与各表 LEFT JOIN 聚合。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| days | `int` | ❌ | `7` | 向前追溯的天数，默认 7 天，最大建议不超过 30 |

**返回：**

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `date` | `str` | 日期，格式 `YYYY-MM-DD` |
| `new_shops` | `int` | 当日新增活跃店铺数 |
| `new_users` | `int` | 当日新增活跃用户数 |
| `new_interactions` | `int` | 当日新增一级评论 + 二级回复 + 问题 + 回答总数 |
| `new_questions` | `int` | 当日新增问题数 |

**返回示例：**

```python
[
    {"date": "2026-06-04", "new_shops": 2, "new_users": 5, "new_interactions": 14, "new_questions": 3},
    {"date": "2026-06-05", "new_shops": 1, "new_users": 3, "new_interactions": 8, "new_questions": 1},
    {"date": "2026-06-06", "new_shops": 0, "new_users": 7, "new_interactions": 21, "new_questions": 5},
    ...
]
```

**业务场景：**
- 管理后台数据趋势折线图
- 近 N 天平台活跃度走势分析

**实现逻辑（概述）：**
使用 `WITH RECURSIVE CTE` 生成从 `CURDATE() - N 天` 到 `CURDATE()` 的连续日期序列，再 `LEFT JOIN` shops / users / shop_comments / comment_replies / shop_questions / question_answers 各表，按日期分组聚合。

**注意事项：**
- 依赖 MySQL 8+ 的 `WITH RECURSIVE` 语法，**不支持 MySQL 5.x**
- `days` 建议不超过 30，过大查询时间会显著增长

---

### `count_shops_by_dict_data(dict_data_ids)` — 按字典标签统计店铺数

传入一组 `DictData` 的 ID，统计每个标签关联的活跃且未封禁的店铺数量。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| dict_data_ids | `list[int]` | ✅ | `DictData` 主键 ID 列表 |

**返回：**

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `dict_data_id` | `int` | 字典数据 ID |
| `dict_data_name` | `str` | 字典数据名称（如 `"火锅"`） |
| `shop_count` | `int` | 关联的活跃且未封禁店铺数，按数量倒序 |

**返回示例：**

```python
[
    {"dict_data_id": 1, "dict_data_name": "火锅", "shop_count": 12},
    {"dict_data_id": 2, "dict_data_name": "烧烤", "shop_count": 8},
    {"dict_data_id": 3, "dict_data_name": "快餐", "shop_count": 5},
]
```

**业务场景：**

```python
# 统计品类分布（Service 层自行传入品类类型的 DictData IDs）
cat_ids = await DictDataDAO.get_ids_by_type_name('品类')
dist = await AnalyticsDAO.count_shops_by_dict_data(cat_ids)

# 统计区域分布（Service 层自行传入区域类型的 DictData IDs）
area_ids = await DictDataDAO.get_ids_by_type_name('区域')
dist = await AnalyticsDAO.count_shops_by_dict_data(area_ids)
```

**实现逻辑（概述）：**
使用原生 SQL，对 `dict_rels` 表按 `dict_data_id` 分组，JOIN `dict_data` 获取名称，JOIN `shops` 过滤活跃且未封禁记录，按 `shop_count` 倒序排列。

**注意事项：**
- **DAO 层不做业务语义假设**，传品类 ID 出品类分布，传区域 ID 出区域分布，语义由调用方决定
- 若传入空列表，直接返回空列表，不触发 SQL

---

### `get_top_rated_shops(limit)` — 评分最高店铺 TOP N

返回评分最高的活跃且未封禁店铺列表，按 `average_rating` 倒序，`favorite_count` 作为二级排序。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| limit | `int` | ❌ | `10` | 返回条数上限 |

**返回：**

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `id` | `int` | 店铺 ID |
| `name` | `str` | 店铺名称 |
| `average_rating` | `float` | 平均评分 |

**返回示例：**

```python
[
    {"id": 42, "name": "老麦快餐", "average_rating": 4.8},
    {"id": 15, "name": "华农火锅", "average_rating": 4.6},
    {"id": 7,  "name": "泰山区烧烤", "average_rating": 4.5},
]
```

**业务场景：**
- 管理后台「评分榜单」展示
- 首页「热门推荐」数据源

**实现逻辑（概述）：**
使用 Tortoise ORM 查询 `Shops.filter(is_active=True, is_banned=False, average_rating__gt=0)`，按 `average_rating` 倒序、`favorite_count` 二级排序，取前 `limit` 条。

---

### `get_most_favorited_shops(limit)` — 收藏最多店铺 TOP N

返回被收藏次数最多的活跃且未封禁店铺列表，按 `favorite_count` 倒序。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| limit | `int` | ❌ | `10` | 返回条数上限 |

**返回：**

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `id` | `int` | 店铺 ID |
| `name` | `str` | 店铺名称 |
| `favorite_count` | `int` | 被收藏次数 |

**返回示例：**

```python
[
    {"id": 42, "name": "老麦快餐", "favorite_count": 128},
    {"id": 15, "name": "华农火锅", "favorite_count": 95},
    {"id": 7,  "name": "泰山区烧烤", "favorite_count": 73},
]
```

**业务场景：**
- 管理后台「收藏榜单」展示
- 首页「最受欢迎店铺」数据源

**实现逻辑（概述）：**
使用 Tortoise ORM 查询 `Shops.filter(is_active=True, is_banned=False)`，按 `favorite_count` 倒序，取前 `limit` 条。

---

### `get_pending_counts()` — 待处理工单数量

返回各状态为 `pending` 的反馈工单（Feedback）数量。

**参数：** 无

**返回：**

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `pending_complaints` | `int` | 类型为 `complaint` 且状态为 `pending` 的工单数 |
| `pending_edit_requests` | `int` | 类型为 `edit_request` 且状态为 `pending` 的工单数 |

**返回示例：**

```python
{"pending_complaints": 3, "pending_edit_requests": 1}
```

**业务场景：**
- 管理后台顶部导航栏工单提醒徽标
- 管理员首页「待处理」数据源

**实现逻辑（概述）：**
通过两条独立 Tortoise ORM `.count()` 查询分别统计两种类型的 pending 工单数。

---

## 典型用法汇总

```python
from dao import AnalyticsDAO

# 1. 管理后台首页 — 平台概览
overview = await AnalyticsDAO.get_overview()
# {"total_shops": 128, "total_users": 3450, "total_comments": 8720, ...}

# 2. 数据趋势 — 近 30 天每日新增
trends = await AnalyticsDAO.get_daily_trends(days=30)
for day in trends:
    print(day["date"], day["new_shops"], day["new_interactions"])

# 3. 品类分布统计（需先从 DictDataDAO 获取品类 ID 列表）
cat_ids = await DictDataDAO.get_ids_by_type_name('品类')
distribution = await AnalyticsDAO.count_shops_by_dict_data(cat_ids)
# [{"dict_data_id": 1, "dict_data_name": "火锅", "shop_count": 12}, ...]

# 4. 评分榜单 TOP 10
top_shops = await AnalyticsDAO.get_top_rated_shops(limit=10)

# 5. 收藏榜单 TOP 10
fav_shops = await AnalyticsDAO.get_most_favorited_shops(limit=10)

# 6. 待处理工单数（管理员 badge）
pending = await AnalyticsDAO.get_pending_counts()
# {"pending_complaints": 3, "pending_edit_requests": 1}
```

---

## 注意事项

1. **`get_daily_trends` 依赖 MySQL 8+ WITH RECURSIVE CTE**，不支持 MySQL 5.x，生产环境需确认 MySQL 版本。
2. **`get_overview` 的 `avg_rating`**：当没有任何店铺有评分时返回 `None`，Service 层应处理为 `"暂无评分"` 展示。
3. **`count_shops_by_dict_data` 不做业务假设**，传什么类型的 DictData ID 就出什么类型的统计，语义由调用方决定。
4. **`dict_data_ids` 为空时直接返回空列表**，不会触发 SQL 查询，调用方无需额外判空。
5. 所有统计方法均只统计 `is_active=True` 且 `is_banned=False`（店铺表）的记录，已删除/封禁数据不计入。
6. `get_top_rated_shops` 仅包含 `average_rating > 0` 的店铺，无评分的店铺不参与排序。