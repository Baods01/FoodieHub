# view_history_dao.py — 浏览历史数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/view_history_dao.py`
> 对应模型：`models/history.py` → `ViewHistory`

---

## 概述

`ViewHistoryDAO` 提供浏览历史表的完整数据访问。

每用户-店铺对只有一条记录，通过 `(user_id, shop_id)` 唯一约束保证。用户重复访问同一店铺时，`viewed_at` 自动更新为当前时间。

---

## 数据模型预览

### ViewHistory — 浏览历史表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 自增主键 |
| user | FK → Users | 浏览用户 |
| shop | FK → Shops | 被浏览店铺 |
| viewed_at | DATETIME | 最近浏览时间（auto_now=True） |
| is_active | BOOLEAN | 软删除标记（继承自 BaseModel） |

---

## 方法概览

### 查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `list_by_user(user_id, page, page_size)` | `page`/`page_size` 默认 1/20 | `dict` | 用户浏览历史列表（分页，按浏览时间倒序） |

### 写操作

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `upsert(user_id, shop_id)` | — | `ViewHistory` | 记录或更新浏览历史 |
| `delete(view_history_id)` | `int` | `bool` | 软删除单条历史记录 |
| `clear_by_user(user_id)` | `int` | `int` | 清空用户所有浏览历史 |

---

## 方法详述

### 查询

---

#### `list_by_user(user_id, page, page_size)` — 用户浏览历史列表（分页）

获取指定用户的所有浏览历史记录，按最近浏览时间倒序分页返回。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | `int` | ✅ | — | 用户 ID |
| page | `int` | ❌ | `1` | 页码（从 1 开始） |
| page_size | `int` | ❌ | `20` | 每页条数 |

**返回：**

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `items` | `List[ViewHistory]` | 当前页的浏览历史记录列表 |
| `total` | `int` | 符合条件的记录总条数 |
| `page` | `int` | 当前页码 |
| `page_size` | `int` | 每页条数 |

**使用示例：**

```python
result = await ViewHistoryDAO.list_by_user(user_id=1, page=1, page_size=20)
for record in result["items"]:
    print(record.shop.name, record.viewed_at)
# total=50, page=1, page_size=20
```

**关联预加载：**
- `shop` 字段已通过 `select_related("shop")` 预加载，可直接访问 `record.shop.name`。

**业务场景：**
- 用户个人主页「最近浏览」列表
- 浏览历史页面分页加载

---

### 写操作

---

#### `upsert(user_id, shop_id)` — 记录或更新浏览历史

新建或更新浏览历史记录。若用户-店铺对已存在，则更新 `viewed_at` 时间；否则新建记录。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| user_id | `int` | ✅ | 用户 ID |
| shop_id | `int` | ✅ | 店铺 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `ViewHistory` | 返回浏览历史 Tortoise 模型实例 |

**使用示例：**

```python
record = await ViewHistoryDAO.upsert(user_id=1, shop_id=42)
print(record.viewed_at)
```

**业务场景：**
- 用户进入店铺详情页时调用，记录一次浏览
- 每次进入店铺详情页都会触发，若已存在则更新时间

**实现逻辑（概述）：**
调用 `ViewHistory.get_or_create()` 尝试获取或创建记录，若记录已存在则调用 `save(update_fields=["viewed_at"])` 更新浏览时间。

---

#### `delete(view_history_id)` — 软删除单条历史记录

将指定浏览历史记录标记为已删除（`is_active=False`）。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| view_history_id | `int` | ✅ | 浏览历史记录 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `bool` | 删除成功返回 `True`；记录不存在返回 `False` |

**使用示例：**

```python
ok = await ViewHistoryDAO.delete(view_history_id=99)
if not ok:
    raise ValueError("浏览记录不存在")
```

**业务场景：**
- 用户主动删除某条浏览历史

**实现逻辑（概述）：**
查询 `is_active=True` 的记录，若存在则置 `is_active=False` 后保存。

---

#### `clear_by_user(user_id)` — 清空用户所有浏览历史

将指定用户的所有浏览历史记录软删除。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| user_id | `int` | ✅ | 用户 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `int` | 被清除的记录条数 |

**使用示例：**

```python
count = await ViewHistoryDAO.clear_by_user(user_id=1)
print(f"已清除 {count} 条浏览记录")
```

**业务场景：**
- 用户注销账户时清空所有浏览历史

**实现逻辑（概述）：**
批量执行 `UPDATE ... SET is_active=False WHERE user_id=X AND is_active=True`，返回受影响行数。

---

## 典型用法汇总

```python
from dao import ViewHistoryDAO

# 1. 用户进入店铺详情页 — 记录浏览
record = await ViewHistoryDAO.upsert(user_id=user.id, shop_id=shop.id)

# 2. 个人主页 — 浏览历史列表
result = await ViewHistoryDAO.list_by_user(user_id=user.id, page=1, page_size=20)
for record in result["items"]:
    print(record.shop.name, record.viewed_at)

# 3. 删除单条浏览历史
ok = await ViewHistoryDAO.delete(view_history_id=99)

# 4. 用户注销 — 清空全部浏览历史
count = await ViewHistoryDAO.clear_by_user(user_id=user.id)
print(f"已清空 {count} 条记录")
```

---

## 注意事项

1. **`list_by_user` 已预加载 `shop` 实体**，可直接访问 `record.shop.name`，无需额外查询。
2. **`upsert` 利用数据库唯一约束实现幂等**，同一用户对同一店铺多次访问只会创建一条记录，后续调用自动更新 `viewed_at`。
3. **删除和清空操作均为软删除**，数据仍保留在数据库中，仅 `is_active=False` 标记。
4. **`clear_by_user` 返回清除的实际条数**，可用于日志或提示用户。