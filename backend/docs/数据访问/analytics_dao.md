# analytics_dao.py — 统计分析数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/analytics_dao.py`

---

## 概述

analytics_dao 提供管理后台所需的聚合统计数据。复杂聚合使用 raw SQL（WITH RECURSIVE CTE、标量子查询等），不包含业务语义（不出现"品类""区域"等词汇）。

---

## 方法列表

### raw SQL（复杂）

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_overview()` | — | `dict` | ⭐ 平台概览：一条 SQL 6 个子查询 |
| `get_daily_trends(days)` | 默认 7 | `list[dict]` | ⭐ 每日趋势：WITH RECURSIVE CTE + 多表 LEFT JOIN |

**`get_overview` 返回：**
```python
{"total_shops": 100, "total_users": 50, "total_comments": 300,
 "total_questions": 20, "pending_complaints": 3, "pending_edits": 1,
 "avg_rating": 4.2}
```

**`get_daily_trends` 返回：**
```python
[
    {"date": "2026-05-22", "new_shops": 2, "new_users": 5, "new_comments": 10, "new_questions": 1},
    {"date": "2026-05-23", ...},
    ...
]
```

### 字典参数聚合

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `count_shops_by_dict_data(dict_data_ids)` | DictData ID 列表 | `list[dict]` | ⭐ 按字典标签统计店铺数 |

**用法示例（Service 层）：**
```python
# 品类分布
cat_ids = await DictDataDAO.get_ids_by_type_name('品类')
dist = await AnalyticsDAO.count_shops_by_dict_data(cat_ids)
# → [{"dict_data_id": 1, "dict_data_name": "火锅", "shop_count": 12}, ...]

# 区域分布
area_ids = await DictDataDAO.get_ids_by_type_name('区域')
dist = await AnalyticsDAO.count_shops_by_dict_data(area_ids)
```

### ORM 查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_top_rated_shops(limit)` | 默认 10 | `list[dict]` | 评分最高店铺 |
| `get_most_favorited_shops(limit)` | 默认 10 | `list[dict]` | 收藏最多店铺 |
| `get_pending_counts()` | — | `dict` | ⭐ 待处理工单数 |

---

## 注意事项

1. **`get_daily_trends` 依赖 MySQL 8+ WITH RECURSIVE 语法**，MySQL 5.x 不支持。
2. **`get_overview` 的 `avg_rating`**：当没有任何评分时返回 `None`，Service 层应处理为 `"暂无"`。
3. **`count_shops_by_dict_data` 不做业务假设**，传品类 ID 出品类分布，传区域 ID 出区域分布——由 Service 层决定语义。
