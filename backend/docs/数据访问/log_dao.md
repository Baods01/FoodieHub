# log_dao.py — 统一操作日志数据访问层

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/log_dao.py`
> 对应模型：`models/logs.py` → `OperationLog`

---

## 概述
`LogDAO` 负责 OperationLog 表的写入和查询。OperationLog 统一记录所有用户（含管理员）的操作行为，用于留档。日志为追加写入，API 不提供任何删除/修改接口。DAO 层不跨表 JOIN，查询结果均为 OperationLog 记录本身。

---

## 数据模型预览
### OperationLog — 统一操作日志
| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BigIntField (pk) | 日志唯一标识 |
| operator_id | FK → Users (nullable) | 操作用户ID（未登录可为空） |
| operator_name | CharField (nullable) | 操作时用户名（冗余存储，用户删除后保留追溯） |
| action | CharField | 操作动作，如 view_shop / comment / ban_user / approve_edit 等 |
| target_type | CharField | 操作对象类型，如 shop / user / comment / complaint 等 |
| target_id | IntField (nullable) | 操作对象ID |
| detail | JSONField (nullable) | 操作详情，如 before/after 快照、封禁原因等 |
| ip_address | CharField (nullable) | 客户端IP地址 |
| user_agent | TextField (nullable) | 客户端设备信息 |
| session_id | CharField (nullable) | 会话ID（未登录用户追踪用） |
| created_at | DatetimeField | 创建时间 |
| updated_at | DatetimeField | 最后更新时间 |
| is_active | BooleanField | 是否启用（软删除，仅供系统内部维护） |

---

## 方法概览
### 写入
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| log | action, operator, operator_name, target_type, target_id, detail, ip_address, user_agent, session_id | OperationLog | 记录一条操作日志 |

### 查询
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|:---|
| get_by_id | id | Optional[OperationLog] | 按ID查询单条日志详情 |
| list | action, target_type, target_id, operator_id, start_time, end_time, page, page_size | dict | 条件筛选分页列表 |
| get_user_view_logs | user_id, action, page, page_size | dict | 获取用户某类操作的历史记录 |

### 统计
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|:---|
| count_by_action | start_time, end_time | List[dict] | 统计各操作类型的数量 |

---

## 方法详述

### log — 记录操作日志

**描述：** 写入一条操作日志。operator 参数支持多种传入形式，自动识别并提取用户ID和用户名。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| action | str | 是 | - | 操作动作名称，如 `view_shop`、`comment`、`ban_user` |
| operator | Any | 否 | None | 操作者，支持：Tortoise 模型实例 / Pydantic 模型 / int（用户ID） / None |
| operator_name | Optional[str] | 否 | None | 操作者用户名（当 operator 为 int 时必传；其他形式可自动提取） |
| target_type | Optional[str] | 否 | None | 操作对象类型，如 `shop`、`user`、`comment` |
| target_id | Optional[int] | 否 | None | 操作对象ID |
| detail | Optional[dict] | 否 | None | 操作详情JSON，如 `{"before": {}, "after": {}}` |
| ip_address | Optional[str] | 否 | None | 客户端IP地址 |
| user_agent | Optional[str] | 否 | None | 客户端设备信息字符串 |
| session_id | Optional[str] | 否 | None | 会话ID（未登录用户追踪用） |

**返回：**
| 类型 | 说明 |
|:---|:---|
| OperationLog | 新创建的 OperationLog 模型实例（未序列化） |

**使用示例：**
```python
# 传入 Tortoise ORM 模型实例
await LogDAO.log(action="view_shop", operator=user_obj, target_type="shop", target_id=10)

# 传入 Pydantic 模型
await LogDAO.log(action="comment", operator=user_response, target_type="shop_comment", target_id=99)

# 传入 int（需显式传 operator_name）
await LogDAO.log(action="ban_user", operator=42, operator_name="admin_zhang", target_type="user", target_id=7)

# 系统自动操作
await LogDAO.log(action="daily_cleanup", detail={"task": "expire_sessions"})
```

**业务场景：**
- 用户浏览店铺：Router 层调用 `LogDAO.log(operator=user, action="view_shop", target_type="shop", target_id=shop_id)`
- 用户评论：Service 层操作成功后 Router 层记录 `comment` 日志
- 管理员封禁用户：Router 层记录 `ban_user` 日志含 `detail={"reason": "违规宣传"}`
- 系统自动任务：operator=None记录系统行为

**实现逻辑（概述）：**
自动识别 operator 类型：Tortoise ORM 实例直接作为 FK 传入；Pydantic 模型或 int提取 `id` 和 `username`；最后统一调用 `OperationLog.create()`。

---

### get_by_id — 按ID查询单条日志

**描述：** 根据日志ID查询单条操作日志详情。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| id | int | 是 | - | 日志ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| Optional[OperationLog] | 找到则返回 OperationLog 实例，未找到或已软删除返回 None |

**使用示例：**
```python
log = await LogDAO.get_by_id(id=12345)
if log:
    print(f"{log.action} by {log.operator_name} at {log.created_at}")
```

**业务场景：**
- 管理后台日志详情查看
- 审计追踪某条具体操作的完整信息

**实现逻辑（概述）：**
调用 `OperationLog.get_or_none(id=id, is_active=True)` 查询。

---

### list — 条件筛选分页日志列表

**描述：** 管理后台按多条件筛选日志列表，分页返回，按创建时间倒序排列。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| action | Optional[str] | 否 | None | 操作动作过滤 |
| target_type | Optional[str] | 否 | None | 操作对象类型过滤 |
| target_id | Optional[int] | 否 | None | 操作对象ID过滤 |
| operator_id | Optional[int] | 否 | None | 操作用户ID过滤 |
| start_time | Optional[datetime] | 否 | None | 创建时间范围起点 |
| end_time | Optional[datetime] | 否 | None | 创建时间范围终点 |
| page | int | 否 | 1 | 页码（从1开始） |
| page_size | int | 否 | 20 | 每页条数 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| dict | 包含 `items`（OperationLog 列表）、`total`（总数）、`page`、`page_size` |

**使用示例：**
```python
result = await LogDAO.list(
    action="ban_user",
    target_type="user",
    operator_id=1,
    start_time=datetime(2026, 1, 1),
    page=1,
    page_size=50,
)
for log in result["items"]:
    print(log.detail)
```

**业务场景：**
- 管理后台日志管理页面：按操作类型、对象类型、时间范围筛选
- 审计用户行为：查看某用户的所有操作记录
- 追踪特定店铺的操作日志

**实现逻辑（概述）：**
构建 `OperationLog.filter(is_active=True)` 链式过滤条件，时间范围用 `created_at__gte` / `created_at__lte`，分页使用 `offset` + `limit`，通过 `prefetch_related("operator")` 预加载操作用户。

---

### get_user_view_logs — 获取用户浏览历史

**描述：** 获取指定用户某类操作（如浏览店铺）的历史记录，按时间倒序排列。**仅返回 OperationLog 本身**，不跨表 JOIN 获取店铺名等信息——需要店铺名等详情时，由 Service 层组合 ShopDAO 查询。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | - | 用户ID |
| action | str | 否 | "view_shop" | 操作类型过滤（默认查浏览记录） |
| page | int | 否 | 1 | 页码（从1开始） |
| page_size | int | 否 | 20 | 每页条数 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| dict | 包含 `items`（OperationLog 列表）、`total`（总数）、`page`、`page_size` |

**使用示例：**
```python
# 获取用户浏览过的店铺列表
result = await LogDAO.get_user_view_logs(user_id=1, action="view_shop", page=1, page_size=10)
logs = result["items"]
# 如需店铺名称等信息，由 Service 层组合 ShopDAO 查询
```

**业务场景：**
- 用户个人中心「最近浏览」页面
- 推荐系统构建用户兴趣画像（基于浏览历史）

**实现逻辑（概述）：**
过滤 `operator_id=user_id + action=action + is_active=True`，按 `created_at` 倒序，分页返回。Service 层可从 `target_id` 获取店铺ID，再调 ShopDAO 补充店铺信息。

---

### count_by_action — 统计各操作类型的数量

**描述：** 统计各操作动作（action）的日志条数，用于管理后台仪表盘展示。按数量降序排列。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| start_time | Optional[datetime] | 否 | None | 统计时间范围起点 |
| end_time | Optional[datetime] | 否 | None | 统计时间范围终点 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| List[dict] | `[{"action": "view_shop", "count": 123}, {"action": "comment", "count": 45}, ...]` |

**使用示例：**
```python
stats = await LogDAO.count_by_action(
    start_time=datetime(2026, 1, 1),
    end_time=datetime(2026, 6, 11),
)
for s in stats:
    print(f"{s['action']}: {s['count']}")
```

**业务场景：**
- 管理后台仪表盘：展示平台各操作类型的频率分布
- 数据分析：了解用户行为热点

**实现逻辑（概述）：**
使用 Tortoise ORM `annotate(count=Count("id")).group_by("action").values("action", "count")` 聚合查询，结果在 Python 层按 `count` 降序排序后返回。