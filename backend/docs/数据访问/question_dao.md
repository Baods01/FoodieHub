# question_dao.py — 问答区数据访问层

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/question_dao.py`
> 对应模型：`models/interaction.py` → `ShopQuestions` / `QuestionAnswers`

---

## 概述
QuestionDAO 负责问答区（ShopQuestions + QuestionAnswers）的全部数据访问操作。该 DAO 处理一级问题（ShopQuestions）和二级回答（QuestionAnswers）的查询、创建、更新、删除，以及点赞计数的原子更新。删除店铺或用户时需通过级联清理方法同步软删除相关问答数据。

---

## 数据模型预览
### ShopQuestions — 一级问题
| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BigIntField (pk) | 问题唯一标识 |
| shop_id | IntField (FK) | 关联店铺 ID，外键 → Shops |
| user_id | IntField (FK) | 提问用户 ID，外键 → Users |
| title | CharField(100) | 问题概括（短标题） |
| content | TextField (nullable) | 问题描述（详细内容，可选） |
| like_count | IntField | 点赞数（冗余字段） |
| is_active | BooleanField | 软删除标记（继承自 BaseModel），默认 True |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

### QuestionAnswers — 二级回答
| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BigIntField (pk) | 回答唯一标识 |
| question_id | BigIntField (FK) | 所属问题 ID，外键 → ShopQuestions |
| user_id | IntField (FK) | 回答用户 ID，外键 → Users |
| content | TextField | 回答内容 |
| reply_to_user_id | IntField (FK, nullable) | 被回复用户 ID（仅用于前端 @username 显示） |
| like_count | IntField | 点赞数（冗余字段） |
| is_active | BooleanField | 软删除标记（继承自 BaseModel），默认 True |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

---

## 方法概览
### ShopQuestions：查询
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id` | question_id: int | `Optional[ShopQuestions]` | 根据 ID 获取问题 |
| `list_by_shop` | shop_id, page, page_size | `dict` | 店铺问题列表，分页 |
| `list_by_user` | user_id, page, page_size | `dict` | 用户问题列表，分页 |
| `count_by_shop` | shop_id | `int` | 统计店铺问题数量 |

### ShopQuestions：写操作
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create` | shop_id, user_id, title, content | `ShopQuestions` | 创建新问题 |
| `update` | question_id, title, content | `Optional[ShopQuestions]` | 更新问题内容 |
| `delete` | question_id: int | `bool` | 软删除问题 |
| `increment_like_count` | question_id: int | `None` | 点赞数 +1（原子操作） |
| `decrement_like_count` | question_id: int | `None` | 点赞数 -1（原子操作） |

### QuestionAnswers：查询
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_answer_by_id` | answer_id: int | `Optional[QuestionAnswers]` | 根据 ID 获取回答 |
| `list_by_question` | question_id: int | `List[QuestionAnswers]` | 问题下的回答列表（按时间正序） |

### QuestionAnswers：写操作
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|:---|
| `create_answer` | question_id, user_id, content, reply_to_user_id | `QuestionAnswers` | 创建回答 |
| `delete_answer` | answer_id: int | `bool` | 软删除回答 |
| `increment_answer_like_count` | answer_id: int | `None` | 回答点赞数 +1（原子操作） |
| `decrement_answer_like_count` | answer_id: int | `None` | 回答点赞数 -1（原子操作） |

### 级联清理
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `clear_by_shop` | shop_id: int | `int` | 软删除店铺下所有问题 |
| `clear_by_user` | user_id: int | `int` | 软删除用户所有问题 |

---

## 方法详述

### get_by_id — 根据ID获取问题

**描述：** 根据问题 ID 获取单条问题记录，预加载提问用户信息。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| question_id | int | 是 | — | 问题 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Optional[ShopQuestions]` | 问题模型实例，不存在或已软删除则返回 None |

**使用示例：**
```python
question = await QuestionDAO.get_by_id(question_id=1)
if question:
    print(f"问题: {question.title}, 提问者: {question.user_id}")
```

**业务场景：**
- 用户点击某问题查看详情时加载问题内容
- 回答提交后跳转到问题详情页

**实现逻辑（概述）：**
调用 `ShopQuestions.get_or_none(id=question_id, is_active=True)` 查询，使用 `prefetch_related("user")` 预加载用户信息。

---

### list_by_shop — 店铺问题列表

**描述：** 获取指定店铺下的所有问题，按时间倒序排列并分页。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| shop_id | int | 是 | — | 店铺 ID |
| page | int | 否 | 1 | 页码，从 1 开始 |
| page_size | int | 否 | 20 | 每页条数 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `dict` | 包含 items（问题列表）、total、page、page_size 的字典 |

**使用示例：**
```python
result = await QuestionDAO.list_by_shop(shop_id=1, page=1, page_size=10)
print(f"共 {result['total']} 个问题")
for q in result["items"]:
    print(f"- {q.title} (点赞 {q.like_count})")
```

**业务场景：**
- 店铺详情页问答区展示该店铺的所有问题
- 问答区首页按店铺筛选问题

**实现逻辑（概述）：**
过滤 `shop_id=shop_id, is_active=True` 后先查总数，再分页查询并预加载 user。

---

### list_by_user — 用户问题列表

**描述：** 获取指定用户提出的所有问题，按时间倒序排列并分页。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | — | 用户 ID |
| page | int | 否 | 1 | 页码，从 1 开始 |
| page_size | int | 否 | 20 | 每页条数 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `dict` | 包含 items（问题列表）、total、page、page_size 的字典 |

**使用示例：**
```python
result = await QuestionDAO.list_by_user(user_id=1, page=1, page_size=10)
```

**业务场景：**
- 用户个人主页展示其提问历史
- "我的提问"页面

**实现逻辑（概述）：**
过滤 `user_id=user_id, is_active=True` 后先查总数，再分页查询并预加载 shop。

---

### count_by_shop — 统计店铺问题数量

**描述：** 统计指定店铺下未被软删除的问题总数。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| shop_id | int | 是 | — | 店铺 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `int` | 问题总数 |

**使用示例：**
```python
count = await QuestionDAO.count_by_shop(shop_id=1)
```

**业务场景：**
- 店铺详情页问答区标题显示问题数量
- 后台统计店铺问答数据

**实现逻辑（概述）：**
过滤条件后调用 Tortoise ORM 的 `.count()` 方法。

---

### create — 创建问题

**描述：** 在指定店铺下创建一个新的问题。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| shop_id | int | 是 | — | 店铺 ID |
| user_id | int | 是 | — | 提问用户 ID |
| title | str | 是 | — | 问题标题（简短概括） |
| content | Optional[str] | 否 | None | 问题详细描述（可选） |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `ShopQuestions` | 创建的问题模型实例 |

**使用示例：**
```python
question = await QuestionDAO.create(
    shop_id=1,
    user_id=1,
    title="这家店的营业时间是什么时候？",
    content="我想周六早上去，不知道几点开门。",
)
```

**业务场景：**
- 用户在店铺详情页发起提问
- Service 层编排创建问题后，通过 signal 自动创建 Activity 动态

**实现逻辑（概述）：**
调用 `ShopQuestions.create(...)` 插入数据库，返回创建的模型实例。

---

### update — 更新问题

**描述：** 更新指定问题的标题和/或内容，仅更新传入的非 None 参数。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| question_id | int | 是 | — | 问题 ID |
| title | Optional[str] | 否 | None | 新标题（传 None 则不更新） |
| content | Optional[str] | 否 | None | 新内容（传 None 则不更新） |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Optional[ShopQuestions]` | 更新后的问题模型实例，不存在则返回 None |

**使用示例：**
```python
question = await QuestionDAO.update(
    question_id=1,
    title="更新后的标题",
    content="更新后的内容",
)
```

**业务场景：**
- 用户编辑自己发布的问题内容
- 管理员协助修改问题标题/内容

**实现逻辑（概述）：**
通过 `get_or_none` 获取问题实例，仅对非 None 的字段进行赋值更新，最后保存。

---

### delete — 软删除问题

**描述：** 软删除指定问题，将 `is_active` 设为 False。该操作不会删除问题的回答（回答需单独处理）。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| question_id | int | 是 | — | 问题 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `bool` | 是否成功删除（问题存在且未被软删除返回 True，否则 False） |

**使用示例：**
```python
success = await QuestionDAO.delete(question_id=1)
```

**业务场景：**
- 用户删除自己发布的问题
- 管理员删除违规问题

**实现逻辑（概述）：**
通过 `get_or_none` 获取问题，设置 `is_active=False` 后保存。

---

### increment_like_count — 问题点赞数 +1

**描述：** 原子递增问题的点赞数，使用数据库 `F()` 表达式避免并发问题。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| question_id | int | 是 | — | 问题 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `None` | 无返回值 |

**使用示例：**
```python
await QuestionDAO.increment_like_count(question_id=1)
```

**业务场景：**
- 用户点赞某个问题时，Service 层调用此方法更新 like_count
- 配合 ContentLikes 表记录点赞行为

**实现逻辑（概述）：**
使用 `ShopQuestions.filter(id=question_id, is_active=True).update(like_count=F("like_count") + 1)` 原子更新。

---

### decrement_like_count — 问题点赞数 -1

**描述：** 原子递减问题的点赞数，使用 `like_count__gt=0` 条件防止计数变为负数。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| question_id | int | 是 | — | 问题 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `None` | 无返回值 |

**使用示例：**
```python
await QuestionDAO.decrement_like_count(question_id=1)
```

**业务场景：**
- 用户取消点赞某个问题时，Service 层调用此方法更新 like_count

**实现逻辑（概述）：**
使用 `filter(id=question_id, is_active=True, like_count__gt=0).update(like_count=F("like_count") - 1)` 原子更新。

---

### get_answer_by_id — 根据ID获取回答

**描述：** 根据回答 ID 获取单条回答记录，预加载回答用户和被回复用户信息。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| answer_id | int | 是 | — | 回答 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Optional[QuestionAnswers]` | 回答模型实例，不存在或已软删除则返回 None |

**使用示例：**
```python
answer = await QuestionDAO.get_answer_by_id(answer_id=1)
if answer:
    print(f"回答内容: {answer.content}, 回复用户: {answer.reply_to_user_id}")
```

**业务场景：**
- 用户点击某回答查看详情
- 回答被删除后验证操作结果

**实现逻辑（概述）：**
调用 `QuestionAnswers.get_or_none(id=answer_id, is_active=True)` 并预加载 user 和 reply_to_user。

---

### list_by_question — 问题下的回答列表

**描述：** 获取指定问题下的所有回答，按时间正序（先回答的在前）排列。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| question_id | int | 是 | — | 问题 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `List[QuestionAnswers]` | 回答模型实例列表 |

**使用示例：**
```python
answers = await QuestionDAO.list_by_question(question_id=1)
for a in answers:
    print(f"- {a.content} (点赞 {a.like_count})")
```

**业务场景：**
- 问题详情页展示所有回答
- 回答排序展示（按时间正序）

**实现逻辑（概述）：**
过滤 `question_id=question_id, is_active=True`，按 `created_at` 正序排列，预加载 user 和 reply_to_user。

---

### create_answer — 创建回答

**描述：** 在指定问题下创建一条新的回答。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| question_id | int | 是 | — | 所属问题 ID |
| user_id | int | 是 | — | 回答用户 ID |
| content | str | 是 | — | 回答内容 |
| reply_to_user_id | Optional[int] | 否 | None | 被回复用户 ID（用于前端 @username 显示） |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `QuestionAnswers` | 创建的回答模型实例 |

**使用示例：**
```python
answer = await QuestionDAO.create_answer(
    question_id=1,
    user_id=2,
    content="这家店早上8点就开门了，晚上10点关门。",
    reply_to_user_id=1,
)
```

**业务场景：**
- 用户在问题详情页提交回答
- Service 层编排创建回答后，通过 signal 自动创建 Activity 动态

**实现逻辑（概述）：**
调用 `QuestionAnswers.create(...)` 插入数据库，返回创建的模型实例。

---

### delete_answer — 软删除回答

**描述：** 软删除指定回答，将 `is_active` 设为 False。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| answer_id | int | 是 | — | 回答 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `bool` | 是否成功删除（回答存在且未被软删除返回 True，否则 False） |

**使用示例：**
```python
success = await QuestionDAO.delete_answer(answer_id=1)
```

**业务场景：**
- 用户删除自己发布的回答
- 管理员删除违规回答

**实现逻辑（概述）：**
通过 `get_or_none` 获取回答，设置 `is_active=False` 后保存。

---

### increment_answer_like_count — 回答点赞数 +1

**描述：** 原子递增回答的点赞数。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| answer_id | int | 是 | — | 回答 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `None` | 无返回值 |

**使用示例：**
```python
await QuestionDAO.increment_answer_like_count(answer_id=1)
```

**业务场景：**
- 用户点赞某回答时更新 like_count

**实现逻辑（概述）：**
使用 `QuestionAnswers.filter(id=answer_id, is_active=True).update(like_count=F("like_count") + 1)` 原子更新。

---

### decrement_answer_like_count — 回答点赞数 -1

**描述：** 原子递减回答的点赞数，防止计数变为负数。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---|:---:|:---:|:---|
| answer_id | int | 是 | — | 回答 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `None` | 无返回值 |

**使用示例：**
```python
await QuestionDAO.decrement_answer_like_count(answer_id=1)
```

**业务场景：**
- 用户取消点赞某回答时更新 like_count

**实现逻辑（概述）：**
使用 `filter(id=answer_id, is_active=True, like_count__gt=0).update(like_count=F("like_count") - 1)` 原子更新。

---

### clear_by_shop — 级联清理店铺下所有问题

**描述：** 删除指定店铺时，批量软删除该店铺下的所有问题。这是店铺删除时级联清理的一部分。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| shop_id | int | 是 | — | 店铺 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `int` | 实际软删除的问题数量 |

**使用示例：**
```python
cleared_count = await QuestionDAO.clear_by_shop(shop_id=1)
```

**业务场景：**
- 删除店铺时，Service 层需同步清理该店铺关联的所有问题
- 管理员删除店铺后的数据清理

**实现逻辑（概述）：**
使用 `ShopQuestions.filter(shop_id=shop_id, is_active=True).update(is_active=False)` 批量更新，返回影响行数。

---

### clear_by_user — 级联清理用户所有问题

**描述：** 删除用户时，批量软删除该用户提出的所有问题。这是用户删除时级联清理的一部分。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | — | 用户 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `int` | 实际软删除的问题数量 |

**使用示例：**
```python
cleared_count = await QuestionDAO.clear_by_user(user_id=1)
```

**业务场景：**
- 用户注销账号时，Service 层需同步软删除其所有问题
- 注意：问题的回答不会因此被软删除（回答属于问题，不属于用户）

**实现逻辑（概述）：**
使用 `ShopQuestions.filter(user_id=user_id, is_active=True).update(is_active=False)` 批量更新。