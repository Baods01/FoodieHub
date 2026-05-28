# analytics_service.py — 统计分析业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/analytics_service.py`

---

## 概述

AnalyticsService 提供管理后台仪表盘所需的聚合统计数据。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_overview()` | — | `dict` | 平台概览（各表总数 + 平均评分） |
| `get_daily_trends(days)` | 默认 7 | `list` | 每日新增趋势 |
| `get_shop_category_distribution()` | — | `list` | 品类分布统计 |
| `get_top_rated_shops(limit)` | 默认 10 | `list` | 评分最高店铺 |
| `get_most_favorited_shops(limit)` | 默认 10 | `list` | 收藏最多店铺 |
| `get_pending_counts()` | — | `dict` | 待处理工单数 |

---

## 典型用法

```python
# 管理后台首页
overview = await AnalyticsService.get_overview()
trends = await AnalyticsService.get_daily_trends(7)
pending = await AnalyticsService.get_pending_counts()
```
