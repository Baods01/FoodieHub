# feedback_dao.py — 统一反馈工单数据访问层

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/feedback_dao.py`
> 对应模型：`models/governance.py` → `Feedback`

---

## 概述
`FeedbackDAO` 负责 Feedback 表的创建、查询、审核操作。该表统一合并了举报（complaint）与勘误（edit_request）两种反馈类型，复用同一套审核流程（pending → approved/rejected）。

---

## 数据模型预览
### Feedback — 统一反馈工单
| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | IntField (pk) | 反馈唯一标识 |
| user_id | FK → Users | 提交用户 |
| type | CharField | complaint=举报 / edit_request=勘误 |
| target_type | CharField | 反馈对象类型：shop / comment / image |
| target_id | IntField | 被反馈对象ID |
| reason_id | FK → DictData | 反馈原因 |
| description | TextField (nullable) | 用户补充说明 |
| status | CharField | pending=待处理 / approved=已采纳 / rejected=已驳回 |
| admin_id | FK → Users (nullable) | 处理管理员 |
| created_at | DatetimeField | 创建时间 |
| updated_at | DatetimeField | 最后更新时间 |
| is_active | BooleanField | 是否启用（软删除） |

---

## 方法概览
### 查询
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| get_by_id | feedback_id: int | Optional[Feedback] | 按ID获取单条反馈详情 |
| list | type, status, target_type, user_id, page, page_size | dict | 条件筛选分页列表 |

### 写操作
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|:---|
| create | user_id, type, target_type, target_id, reason_id, description | Feedback | 新建反馈工单 |
| approve | feedback_id, admin_id | Optional[Feedback] | 管理员通过反馈 |
| reject | feedback_id, admin_id | Optional[Feedback] | 管理员驳回反馈 |

---

## 方法详述

### create — 新建反馈工单

**描述：** 创建一条新的反馈工单，初始状态为 `pending`。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | - | 提交用户ID |
| type | str | 是 | - | 反馈类型：`complaint`（举报）或 `edit_request`（勘误） |
| target_type | str | 是 | - | 被反馈对象类型：`shop` / `comment` / `image` |
| target_id | int | 是 | - | 被反馈对象ID |
| reason_id | int | 是 | - | 反馈原因ID（关联 DictData） |
| description | Optional[str] | 否 | None | 用户填写的补充描述 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| Feedback | 新创建的 Feedback 模型实例（未序列化） |

**使用示例：**
```python
fb = await FeedbackDAO.create(
    user_id=1,
    type="complaint",
    target_type="shop",
    target_id=10,
    reason_id=3,
    description="该店铺环境脏乱差",
)
```

**业务场景：**
- 用户提交举报：举报违规店铺、评论、图片
- 用户提交勘误：修正店铺信息错误

**实现逻辑（概述）：**
直接调用 `Feedback.create()` 插入数据库，初始 `status="pending"`，`admin_id=None`。

---

### get_by_id — 按ID获取反馈详情

**描述：** 根据反馈ID查询单条反馈详情，同时预加载 user、admin、reason 关联。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| feedback_id | int | 是 | - | 反馈工单ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| Optional[Feedback] | 找到则返回 Feedback 实例（含 select_related 预加载），未找到或已软删除返回 None |

**使用示例：**
```python
fb = await FeedbackDAO.get_by_id(feedback_id=5)
if fb:
    print(fb.type, fb.status, fb.description)
```

**业务场景：**
- 管理员查看某条反馈的完整详情
- 反馈处理结果回显给用户

**实现逻辑（概述）：**
调用 `Feedback.get_or_none(id=feedback_id, is_active=True)` 并通过 `select_related("user", "admin", "reason")` 预加载关联对象。

---

### list — 条件筛选分页列表

**描述：** 按多种条件筛选反馈工单列表，支持分页，按创建时间倒序排列。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| type | Optional[str] | 否 | None | 反馈类型过滤：`complaint` 或 `edit_request` |
| status | Optional[str] | 否 | None | 审核状态过滤：`pending` / `approved` / `rejected` |
| target_type | Optional[str] | 否 | None | 被反馈对象类型过滤 |
| user_id | Optional[int] | 否 | None | 提交用户ID过滤 |
| page | int | 否 | 1 | 页码（从1开始） |
| page_size | int | 否 | 20 | 每页条数 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| dict | 包含 `items`（Feedback列表）、`total`（总数）、`page`、`page_size` |

**使用示例：**
```python
result = await FeedbackDAO.list(
    type="complaint",
    status="pending",
    page=1,
    page_size=10,
)
items = result["items"]
total = result["total"]
```

**业务场景：**
- 管理后台反馈列表页：待处理举报优先显示
- 用户个人中心查看自己提交的所有反馈

**实现逻辑（概述）：**
构建 `Feedback.filter(is_active=True)` 链式过滤条件，分页使用 `offset` + `limit`，`select_related` 预加载关联。

---

### approve — 管理员通过反馈

**描述：** 管理员将某条 `pending` 状态的反馈标记为已采纳（approved）。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| feedback_id | int | 是 | - | 反馈工单ID |
| admin_id | int | 是 | - | 处理管理员ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| Optional[Feedback] | 成功则返回更新后的 Feedback 实例；该反馈不存在或非 pending 状态返回 None |

**使用示例：**
```python
fb = await FeedbackDAO.approve(feedback_id=5, admin_id=2)
if fb:
    print(f"反馈 {fb.id} 已采纳")
```

**业务场景：**
- 管理员审核举报：确认店铺违规后采纳处罚
- 管理员审核勘误：确认信息错误后采纳修正

**实现逻辑（概述）：**
先通过 `get_or_none(id=feedback_id, is_active=True, status="pending")` 查询，仅处理待处理状态的反馈；更新 `status="approved"` 和 `admin_id`，调用 `save()` 持久化。

---

### reject — 管理员驳回反馈

**描述：** 管理员将某条 `pending` 状态的反馈标记为已驳回（rejected）。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| feedback_id | int | 是 | - | 反馈工单ID |
| admin_id | int | 是 | - | 处理管理员ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| Optional[Feedback] | 成功则返回更新后的 Feedback 实例；该反馈不存在或非 pending 状态返回 None |

**使用示例：**
```python
fb = await FeedbackDAO.reject(feedback_id=5, admin_id=2)
if fb is None:
    print("该反馈无法驳回（可能已处理）")
```

**业务场景：**
- 管理员驳回无效举报：举报证据不足或不符合规则
- 管理员驳回无效勘误：信息本身无误

**实现逻辑（概述）：**
逻辑同 `approve`，区别在于将 `status` 更新为 `"rejected"`。