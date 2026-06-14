# like_dao.py — 内容点赞数据访问层

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/like_dao.py`
> 对应模型：`models/interaction.py` → `ContentLikes`

---

## 概述
`LikeDAO` 负责 ContentLikes 表的全套操作。该表采用多态设计（entity_type + entity_id），统一管理 ShopComments、CommentReplies、ShopQuestions、QuestionAnswers 四种内容的点赞/取消点赞。DAO 层只操作 ContentLikes 本身，**不**处理各内容冗余字段 `like_count` 的同步（由 Service 层负责）。

---

## 数据模型预览
### ContentLikes — 内容点赞表（多态关联）
| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BigIntField (pk) | 点赞唯一标识 |
| user_id | FK → Users | 点赞用户 |
| entity_type | CharField | 被点赞内容类型：shop_comment / comment_reply / shop_question / question_answer |
| entity_id | BigIntField | 被点赞内容ID |
| created_at | DatetimeField | 点赞时间 |
| updated_at | DatetimeField | 最后更新时间 |
| is_active | BooleanField | 是否启用（True=已点赞，False=已取消） |

---

## 方法概览
### 查询
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| is_liked | user_id, entity_type, entity_id | bool | 检查用户是否已点赞某内容 |
| get_by_entity | entity_type, entity_id | List[ContentLikes] | 获取某内容的所有点赞记录 |
| count_by_entity | entity_type, entity_id | int | 某内容的点赞总数 |
| get_by_user | user_id, page, page_size | dict | 某用户的所有点赞记录（分页） |

### 写操作
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|:---|
| like | user_id, entity_type, entity_id | dict | 执行点赞（含软删除恢复逻辑） |
| unlike | user_id, entity_type, entity_id | dict | 取消点赞（软删除） |
| toggle | user_id, entity_type, entity_id | dict | 一键切换点赞状态 |

### 级联清理
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|:---|
| clear_entity_likes | entity_type, entity_id | int | 软删除某内容的所有点赞记录 |

---

## 方法详述

### is_liked — 检查用户是否已点赞

**描述：** 检查指定用户是否已对某内容（实体）点赞（is_active=True）。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | - | 用户ID |
| entity_type | str | 是 | - | 被点赞内容类型 |
| entity_id | int | 是 | - | 被点赞内容ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| bool | True=已点赞，False=未点赞或已取消 |

**使用示例：**
```python
is_liked = await LikeDAO.is_liked(user_id=1, entity_type="shop_comment", entity_id=100)
```

**业务场景：**
- 前端展示点赞按钮的选中状态
- 点赞操作前预检查，避免无效请求

**实现逻辑（概述）：**
调用 Tortoise ORM `.exists()` 查询 `user_id + entity_type + entity_id + is_active=True` 是否存在。

---

### get_by_entity — 获取某内容的所有点赞记录

**描述：** 获取指定内容（实体）的所有有效点赞记录，按点赞时间升序排列。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| entity_type | str | 是 | - | 被点赞内容类型 |
| entity_id | int | 是 | - | 被点赞内容ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| List[ContentLikes] | ContentLikes 模型实例列表 |

**使用示例：**
```python
likes = await LikeDAO.get_by_entity(entity_type="shop_comment", entity_id=100)
for like in likes:
    print(like.user_id, like.created_at)
```

**业务场景：**
- 查看某条评论的所有点赞用户列表
- 管理后台查看某问题的点赞明细

**实现逻辑（概述）：**
过滤 `entity_type + entity_id + is_active=True`，按 `created_at` 升序排列返回。

---

### count_by_entity — 统计某内容的点赞总数

**描述：** 返回指定内容（实体）的有效点赞总数。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| entity_type | str | 是 | - | 被点赞内容类型 |
| entity_id | int | 是 | - | 被点赞内容ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| int | 点赞总数 |

**使用示例：**
```python
count = await LikeDAO.count_by_entity(entity_type="shop_question", entity_id=5)
```

**业务场景：**
- 获取问题的点赞数展示
- Service 层用于同步各内容冗余字段 like_count（仅作参考，实际以 like_count 字段为准）

**实现逻辑（概述）：**
调用 `.count()` 统计 `entity_type + entity_id + is_active=True` 的记录数。

---

### get_by_user — 获取用户点赞记录（分页）

**描述：** 获取指定用户的所有点赞记录（分页），按点赞时间倒序排列。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | - | 用户ID |
| page | int | 否 | 1 | 页码（从1开始） |
| page_size | int | 否 | 20 | 每页条数 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| dict | 包含 `items`（ContentLikes 列表）、`total`（总数）、`page`、`page_size` |

**使用示例：**
```python
result = await LikeDAO.get_by_user(user_id=1, page=1, page_size=20)
items = result["items"]
total = result["total"]
```

**业务场景：**
- 用户个人中心「我的点赞」页面
- 点赞列表翻页加载

**实现逻辑（概述）：**
过滤 `user_id + is_active=True`，分页使用 `offset` + `limit`，按 `created_at` 倒序排列。

---

### like — 执行点赞

**描述：** 执行点赞操作。若该用户对同一内容存在软删除记录（is_active=False），则将其恢复；否则新建一条点赞记录。返回 `{"action": "liked"}` 供 Service 层决策是否对目标内容的 `like_count` 做 +1 操作。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | - | 用户ID |
| entity_type | str | 是 | - | 被点赞内容类型 |
| entity_id | int | 是 | - | 被点赞内容ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| dict | `{"action": "liked"}` |

**使用示例：**
```python
result = await LikeDAO.like(user_id=1, entity_type="shop_comment", entity_id=100)
if result["action"] == "liked":
    # Service 层此处可执行 like_count +1
    await ShopCommentService.increment_like_count(entity_id=100)
```

**业务场景：**
- 用户点击点赞按钮
- Service 层根据 action 同步更新目标内容的 like_count 冗余字段

**实现逻辑（概述）：**
先查询是否存在 `user_id + entity_type + entity_id` 的记录（含软删除）；若存在但 `is_active=False` 则恢复（设为 True）；若不存在则新建。始终返回 `{"action": "liked"}`。

---

### unlike — 取消点赞

**描述：** 将指定用户的点赞记录软删除（is_active=False）。若原本就没有点赞记录，返回 `{"action": "none"}`。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | - | 用户ID |
| entity_type | str | 是 | - | 被取消点赞内容类型 |
| entity_id | int | 是 | - | 被取消点赞内容ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| dict | `{"action": "unliked"}` 或 `{"action": "none"}`（原本未点赞） |

**使用示例：**
```python
result = await LikeDAO.unlike(user_id=1, entity_type="shop_comment", entity_id=100)
if result["action"] == "unliked":
    # Service 层此处可执行 like_count -1
    await ShopCommentService.decrement_like_count(entity_id=100)
```

**业务场景：**
- 用户再次点击已点赞的内容（取消点赞）
- Service 层根据 action 同步更新目标内容的 like_count 冗余字段

**实现逻辑（概述）：**
查询 `user_id + entity_type + entity_id + is_active=True` 记录；若存在则 `is_active=False` 并保存；若不存在则返回 `{"action": "none"}`。

---

### toggle — 一键切换点赞状态

**描述：** 根据当前点赞状态自动切换点赞/取消点赞，是 `like` 和 `unlike` 的合并操作。返回操作类型及当前点赞状态，供 Service 层决策 `like_count` 的增减。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | - | 用户ID |
| entity_type | str | 是 | - | 被操作内容类型 |
| entity_id | int | 是 | - | 被操作内容ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| dict | `{"action": "liked"|"unliked", "is_liked": bool}` |

**使用示例：**
```python
result = await LikeDAO.toggle(user_id=1, entity_type="shop_comment", entity_id=100)
# result: {"action": "liked", "is_liked": True} 或 {"action": "unliked", "is_liked": False}
if result["action"] == "liked":
    await ShopCommentService.increment_like_count(entity_id=100)
else:
    await ShopCommentService.decrement_like_count(entity_id=100)
```

**业务场景：**
- 前端点赞按钮点击事件（无需预判断当前状态）
- 同时处理新增点赞和取消点赞的 Service 层联动

**实现逻辑（概述）：**
查询 `user_id + entity_type + entity_id` 记录：若 `is_active=True` → 取消点赞并返回 unliked；若 `is_active=False` → 恢复点赞并返回 liked；若不存在 → 新建并返回 liked。

---

### clear_entity_likes — 级联清理某内容的所有点赞

**描述：** 在删除某内容（实体）时，作为级联清理的一部分，将该内容的所有点赞记录软删除。返回影响记录数。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| entity_type | str | 是 | - | 被清理内容类型 |
| entity_id | int | 是 | - | 被清理内容ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| int | 被软删除的点赞记录数量 |

**使用示例：**
```python
count = await LikeDAO.clear_entity_likes(entity_type="shop_comment", entity_id=100)
print(f"清理了 {count} 条点赞记录")
```

**业务场景：**
- 删除评论时同步清理该评论的所有点赞（ContentLikes 级联清理要求）
- 删除问题时同步清理该问题的所有点赞

**实现逻辑（概述）：**
使用 `update(is_active=False)` 批量软删除 `entity_type + entity_id + is_active=True` 的所有记录，返回更新行数。