# history_service.py — 浏览历史业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/history_service.py`

---

## 概述

HistoryService 将 LogDAO 返回的浏览日志（OperationLog 记录）与 ShopsDAO 查询到的店铺信息拼接，返回前端可直接渲染的 `ViewHistoryItem` 格式。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_view_history(user_id, page, page_size)` | | `dict` | 用户浏览历史，附带 shop_name / shop_cover |
| `delete(history_id)` | `int` | `bool` | 删除单条历史记录，软删除（is_active=False） |
| `clear(user_id)` | `int` | `int` | 清空用户全部历史记录，返回删除数量 |

---

## 返回格式

```json
{
    "items": [
        {
            "id": 1,
            "shop_id": 15,
            "shop_name": "陈记糖水铺",
            "shop_cover": "/static/images/xxx.jpg",
            "region": null,
            "viewed_at": "2026-05-29T14:30:00"
        }
    ],
    "total": 42,
    "has_more": true
}
```

---

## 依赖关系

```
Router → HistoryService → LogDAO.get_user_view_logs()
                        → ShopsDAO.get_by_id()  ← 每条记录查一次店铺
```

---

## 注意事项

- 每条浏览记录会额外执行一次 `ShopsDAO.get_by_id()` 查询
- 如对应店铺已被删除，`shop_name` 显示为 `"已删除的店铺"`
- `region` 当前始终为 `None`（后端未从 dict_data 中提取区域名）
- 分页返回 `has_more` 而非原 `page`/`page_size`，前端可直接用
