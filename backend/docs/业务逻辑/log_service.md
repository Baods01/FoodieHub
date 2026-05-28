# log_service.py — 操作日志业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/log_service.py`

---

## 概述

LogService 提供操作日志的写入和查询，以及每日趋势数据。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `log(action, operator, target_type, target_id, detail, ...)` | action 必填 | `None` | ⭐ 业务操作收尾时调用 |
| `get_logs(action, target_type, operator_id, page, page_size)` | 筛选可选 | `dict` | 管理后台日志列表 |
| `get_daily_trends(days)` | 默认 7 | `list` | 每日新增趋势 |

---

## 典型用法

```python
# 在 Service 方法末尾记录日志
await LogService.log(
    action="ban_shop",
    operator=admin_user,
    target_type="shop",
    target_id=shop.id,
    detail={"reason": "违规内容"},
)
```
