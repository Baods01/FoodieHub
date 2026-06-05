# complaint_dao.py — 举报数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/complaint_dao.py`

---

## 概述

complaint_dao 提供 Complaints 表的完整访问。与 EditRequestDAO 保持一致的治理工单设计（用户提交 → admin 审核 → 结果写入）。

---

## 方法列表

### 查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(complaint_id)` | | `Optional[Complaints]` | prefetch user + admin |
| `list(status, user_id, page, page_size)` | 全部可选 | `dict` | ⭐ 管理后台筛选分页 |
| `has_pending_complaint(user_id, complainant_type, complainant_id)` | | `bool` | ⭐ 重复举报检测 |
| `get_count_by_status()` | | `dict` | 仪表盘统计 |

### 写入

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create(user_id, complainant_type, complainant_id, reason_code, description)` | description 可选 | `Complaints` | |
| `approve(complaint_id, admin_id, action, result_description)` | | `Optional[Complaints]` | ⭐ 审核通过 |
| `reject(complaint_id, admin_id, result_description)` | | `Optional[Complaints]` | ⭐ 驳回 |
| `delete(complaint_id)` | | `bool` | |

---

## 典型用法

```python
from dao import ComplaintDAO, MessageDAO, LogDAO

# 用户举报
complaint = await ComplaintDAO.create(
    user_id=user.id, complainant_type="comment",
    complainant_id=123, reason_code="spam",
)

# 管理员审核通过
await ComplaintDAO.approve(complaint.id, admin.id, "delete_comment", "已删除违规评论")
# 通知举报人 + 记录日志（Service 层完成）
```

---

## 注意事项

1. **`approve` 和 `reject` 只更新状态**，实际执行治理操作（删评论/封店铺）是 Service 层在调 DAO 后完成的。
2. **`has_pending_complaint` 仅检查 `status='pending'` 的记录**，已处理的举报不影响再次提交。
