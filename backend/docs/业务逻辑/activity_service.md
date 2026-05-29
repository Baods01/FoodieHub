# activity_service.py — 动态业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/activity_service.py`

---

## 概述

ActivityService 是动态时间线的业务封装层。DAO 返回的 Activities 模型实例已通过 `.prefetch_related("shop")` 预加载了关联店铺，Service 从中提取 `shop_name` 拼入响应，避免前端逐个按 shop_id 查询。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `list_by_user(user_id, page, page_size)` | | `dict` | ⭐ 用户动态时间线，附带 shop_name |

---

## 返回格式

```json
{
    "items": [
        {
            "id": 1,
            "user_id": 3,
            "type": "comment",
            "target_id": 42,
            "target_type": "shop_comment",
            "content": null,
            "shop_id": 15,
            "shop_name": "陈记糖水铺",
            "created_at": "2026-05-29T10:00:00"
        }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
}
```

---

## 依赖关系

```
Router → ActivityService → ActivityDAO → Activities (model)
                                ↓
                          prefetch_related("shop") → Shops (model)
```

- `ActivityDAO.list_by_user()` 通过 `.prefetch_related("shop")` 预加载店铺
- Service 层遍历 items，提取 `item.shop.name` 作为 `shop_name`
- DAO 层无需修改

---

## 注意事项

- `activity.content` 始终为 `null`（`activity_signals.py` 未实现 content 组装）
- `activity.type` 取值：`rating` / `comment` / `reply` / `favorite` / `question`
- `activity.target_type` 更细粒：`shop_comment` / `comment_reply` / `rating` / `favorite` / `shop_question`
