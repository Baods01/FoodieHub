# complaint_service.py — 举报业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/complaint_service.py`

---

## 概述

ComplaintService 提供举报的创建、列表、审核全流程。approve/reject 内嵌 `LogDAO.log()` 记录管理员操作日志。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create(user_id, req)` | req: `ComplaintCreateRequest` | `ComplaintResponse` | 创建举报 |
| `list(status, user_id, page, page_size)` | 筛选可选 | `ComplaintListResponse` | 举报列表 |
| `get_stats()` | — | `ComplaintStatsResponse` | 各状态统计 |
| `approve(complaint_id, admin_id, action, result_description)` | | `Optional[ComplaintResponse]` | ⭐ 审核通过 + 记录日志 |
| `reject(complaint_id, admin_id, result_description)` | | `Optional[ComplaintResponse]` | ⭐ 驳回 + 记录日志 |

---

## 典型用法

```python
# 用户举报
req = ComplaintCreateRequest(complainant_type="comment", complainant_id=123, reason_code="spam")
c = await ComplaintService.create(user.id, req)

# 管理员审核
await ComplaintService.approve(c.id, admin.id, "delete_comment", "已删除违规评论")
```
