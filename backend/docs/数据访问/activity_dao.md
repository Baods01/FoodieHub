# activity_dao.py — 动态数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/activity_dao.py`
> 对应模型：`models/users.py` → `Activities`

---

## 概述

`ActivityDAO` 提供 `Activities`（动态）表的完整访问。动态用于聚合展示用户在平台上的公开行为（评论、评分、收藏、提问等），是用户主页时间线的核心数据源。

---

## 数据模型预览

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| user | FK → Users | 产生动态的用户 |
| type | VARCHAR(50) | 动态类型：`comment` / `rating` / `favorite` / `add_shop` / `reply` / `question` |
| target_id | INT | 关联目标ID（评论ID / 店铺ID 等） |
| target_type | VARCHAR(50) | 目标实体类型，辅助前端判断跳转路径 |
| content | VARCHAR(255) | 预格式化的展示文本，如"评论了店铺" |
| shop | FK → Shops (NULL) | 关联店铺ID，用于前端生成跳转链接 |
| is_active | BOOLEAN | 软删除标记（继承自 BaseModel） |

---

## 方法详述

### `get_by_id(activity_id)` — 按 ID 查询单条动态

根据动态记录 ID 查询一条动态。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| activity_id | `int` | ✅ | 动态记录的主键 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[Activities]` | 找到则返回 Tortoise 模型实例；未找到或已软删除返回 `None` |

**使用示例：**

```python
activity = await ActivityDAO.get_by_id(42)
if activity:
    print(activity.content)   # "评论了店铺"
    print(activity.shop.name)  # 需要 prefetch，这里可能需另查
```

**业务场景：**
- 查看某条动态详情
- 动态删除前的合法性校验

---

### `list_by_user(user_id, page, page_size)` — 用户动态时间线（分页）

获取指定用户的动态列表，按时间倒序排列。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | `int` | ✅ | — | 用户 ID |
| page | `int` | ❌ | `1` | 页码（从 1 开始） |
| page_size | `int` | ❌ | `20` | 每页条数 |

**返回：**

|字段 | 类型 | 说明 |
|:---|:---|:---|
| `items` | `List[Activities]` | 当前页的动态记录列表 |
| `total` | `int` | 符合条件的动态总条数 |
| `page` | `int` | 当前页码 |
| `page_size` | `int` | 每页条数 |

**使用示例：**

```python
result = await ActivityDAO.list_by_user(user_id=1, page=1, page_size=20)
for activity in result["items"]:
    print(activity.type, activity.content)
# total=50, page=1, page_size=20
```

**关联预加载：**
- `shop` 字段已通过 `prefetch_related("shop")` 预加载，可直接访问 `activity.shop.name` 而无需额外查询。

**业务场景：**
- 用户个人主页的时间线展示
- 分页加载更多动态

---

### `create(user_id, type, target_id, target_type, content, shop_id)` — 创建动态

新建一条动态记录。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | `int` | ✅ | — | 产生动态的用户 ID |
| type | `str` | ✅ | — | 动态类型，取值见下方约定 |
| target_id | `int` | ✅ | — | 关联目标的主键 ID |
| target_type | `str` | ✅ | — | 目标实体类型，如 `"shop"` / `"comment"` |
| content | `Optional[str]` | ❌ | `None` | 预格式化的展示文本 |
| shop_id | `Optional[int]` | ❌ | `None` | 关联店铺 ID（用于前端跳转链接） |

**`type` 字段取值约定：**

| type 值 | 含义 | 触发时机示例 |
|:---|:---|:---|
| `comment` | 用户评论了店铺 | 发表一级评论后 |
| `rating` | 用户评分了店铺 | 提交评分后 |
| `favorite` | 用户收藏了店铺 | 收藏/取消收藏操作后 |
| `add_shop` | 用户新增了店铺 | 创建店铺审核通过后 |
| `reply` | 用户回复了评论/回答 | 发表二级回复后 |
| `question` | 用户提问了店铺 | 发表问题后 |
| `answer` | 用户回答了问题 | 回答被采纳后（暂定） |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Activities` | 返回新创建的 Tortoise 模型实例（未序列化） |

**使用示例：**

```python
# 用户评论后创建动态
activity = await ActivityDAO.create(
    user_id=user.id,
    type="comment",
    target_id=comment.id,
    target_type="shop_comment",
    content=f"评论了店铺「{shop.name}」",
    shop_id=shop.id,
)

# 用户评分后创建动态
activity = await ActivityDAO.create(
    user_id=user.id,
    type="rating",
    target_id=rating.id,
    target_type="rating",
    content=f"给「{shop.name}」评了{score}星",
    shop_id=shop.id,
)
```

**业务场景：**
- Service 层在完成评论/评分/收藏等操作后，显式调用 `create` 生成动态
- `content` 由调用方拼接格式化字符串传入

**实现逻辑（概述）：**
内部调用 `Activities.create()`插入数据库，返回新实例。

---

### `delete(activity_id)` — 软删除单条动态

将指定动态标记为已删除（`is_active=False`）。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| activity_id | `int` | ✅ | 动态记录的主键 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `bool` | 删除成功返回 `True`；动态不存在返回 `False` |

**使用示例：**

```python
ok = await ActivityDAO.delete(42)
if not ok:
    raise ValueError("动态不存在")
```

**业务场景：**
- 用户主动删除自己的动态（若有此产品功能）
- 后台管理员删除违规动态

**实现逻辑（概述）：**
查询 `is_active=True` 的记录，若存在则置 `is_active=False` 后保存。

---

### `clear_by_user(user_id)` — 清理用户全部动态

将指定用户的所有动态全部软删除，通常在用户注销时调用。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| user_id | `int` | ✅ | 用户 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `int` | 被清理的动态记录条数 |

**使用示例：**

```python
count = await ActivityDAO.clear_by_user(user_id=99)
print(f"已清理 {count} 条动态")
```

**业务场景：**
- 用户注销账户时，清理该用户的动态记录
- 管理员删除用户时连带清理动态

**实现逻辑（概述）：**
批量执行 `UPDATE ... SET is_active=False WHERE user_id=X AND is_active=True`，返回受影响行数。

---

## 典型用法汇总

```python
from dao import ActivityDAO

# 1. 用户主页 —动态时间线（分页）
result = await ActivityDAO.list_by_user(user_id=user.id, page=1, page_size=20)
for activity in result["items"]:
    print(activity.shop.name) # 已 prefetch，可直接访问

# 2. 发表评论后 — 同步创建动态
activity = await ActivityDAO.create(
    user_id=user.id,
    type="comment",
    target_id=comment.id,
    target_type="shop_comment",
    content=f"评论了店铺「{shop.name}」",
    shop_id=shop.id,
)

# 3. 删除某条动态
ok = await ActivityDAO.delete(activity_id=42)
assert ok

# 4. 用户注销 — 清理全部动态
count = await ActivityDAO.clear_by_user(user_id=user.id)
print(f"清理了 {count} 条")
```

---

## 注意事项

1. **`list_by_user` 已预加载 `shop`**，可直接访问 `activity.shop.name` 用于前端跳转，无需额外查询。
2. **动态由 Service 层显式调用 `create`** 而非自动触发。Service 在完成评论/评分/收藏等操作后，自行调用 `ActivityDAO.create()` 生成动态。
3. **`type` 取值须严格遵循约定**，常见值：`comment` / `rating` / `favorite` / `add_shop` / `reply` / `question`。
4. **`content` 字段为预格式化文本**，由调用方拼接好后传入（如 `"评论了店铺「老麦快餐」"`），DAO 层不做任何拼接。
5. **`shop_id` 用于前端生成跳转链接**，如果动态没有直接关联到某个店铺（如系统公告类动态），可传 `None`。
6. 所有查询方法默认只返回 `is_active=True` 的记录，软删除的动态对业务层不可见。