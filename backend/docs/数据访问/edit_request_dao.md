# edit_request_dao.py — 店铺编辑反馈数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/edit_request_dao.py`

---

## 概述

edit_request_dao 提供 ShopEditRequests 表的完整访问。与 ComplaintDAO 保持一致的治理工单设计。

反馈类型由 `proposed_data.type` 区分：
- `"correction"`：店铺信息勘误
- `"merge"`：重复店铺反馈

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(request_id)` | | `Optional[ShopEditRequests]` | prefetch shop + user + admin |
| `list(status, user_id, shop_id, page, page_size)` | 全部可选 | `dict` | ⭐ 管理后台筛选分页 |
| `create(shop_id, user_id, proposed_data)` | | `ShopEditRequests` | |
| `approve(request_id, admin_id)` | | `Optional[ShopEditRequests]` | ⭐ 审核通过 |
| `reject(request_id, admin_id)` | | `Optional[ShopEditRequests]` | ⭐ 驳回 |
| `delete(request_id)` | | `bool` | |

---

## 典型用法

```python
from dao import EditRequestDAO

# 用户提交勘误
er = await EditRequestDAO.create(
    shop_id=shop.id, user_id=user.id,
    proposed_data={
        "type": "correction",
        "changes": {"name": "正确店名"},
    },
)

# 管理员审核
await EditRequestDAO.approve(er.id, admin.id)
```

---

## 注意事项

1. **`approve`/`reject` 只更新工单状态**，实际的店铺数据修改（如改名、合并）由 Service 层执行。
2. **`list` 支持按 `shop_id` 筛选**，管理后台可查看某店铺的所有勘误历史。
