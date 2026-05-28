# governance_service.py — 勘误/重复反馈业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/governance_service.py`

---

## 概述

GovernanceService 提供店铺勘误和重复反馈的提交、列表、审核全流程。approve/reject 内嵌 `LogDAO.log()` 记录管理员操作日志。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create_edit_request(shop_id, user_id, proposed_data)` | | `EditRequestResponse` | 提交勘误/重复反馈 |
| `list_edit_requests(status, user_id, shop_id, page, page_size)` | 筛选可选 | `EditRequestListResponse` | 管理后台列表 |
| `approve_edit_request(request_id, admin_id)` | | `Optional[EditRequestResponse]` | ⭐ 审核通过 + 日志 |
| `reject_edit_request(request_id, admin_id)` | | `Optional[EditRequestResponse]` | ⭐ 驳回 + 日志 |

---

## 典型用法

```python
# 用户提交勘误
er = await GovernanceService.create_edit_request(
    shop_id=shop.id, user_id=user.id,
    proposed_data={"type": "correction", "changes": {"name": "正确店名"}},
)

# 管理员审核
await GovernanceService.approve_edit_request(er.id, admin.id)
```
