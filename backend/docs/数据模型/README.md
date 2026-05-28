# 食探社 — 数据模型说明文档

> 面向：后端开发人员
> 目的：讲清楚所有数据模型的设计理念、字段含义、关系约束，让开发者无需阅读模型定义文件即可上手开发

---

## 目录

1. [设计总则](#1-设计总则)
2. [文件组织](#2-文件组织)
3. [模型全景关系图](#3-模型全景关系图)
4. [字典体系（dict.py）](#4-字典体系)
5. [用户模块（users.py）](#5-用户模块)
6. [店铺模块（shops.py）](#6-店铺模块)
7. [资源模块（images.py）](#7-资源模块)
8. [互动模块（interaction.py）](#8-互动模块)
9. [治理模块（governance.py）](#9-治理模块)
10. [日志模块（logs.py）](#10-日志模块)
11. [基类（base.py）](#11-基类)
12. [附录](#12-附录)

---

## 1. 设计总则

### 1.1 核心设计理念

| 原则 | 说明 |
|:---|:---|
| **标签字典化** | 所有可枚举的标签属性（品类、区域、就餐方式等）均通过 DictData 字典表管理，不在店铺表上创建硬编码字段 |
| **评论问答分离** | 评论区与问答区各自拆分为两级表，不再用 type 字段混用在一张表里 |
| **扁平回复** | 二级回复之间不嵌套（无 parent_id 自引用），全部平铺在一级内容下，reply_to_user_id 仅用于 @username 前缀展示 |
| **治理工单化** | 举报和勘误反馈采用统一的 "用户提交 → 管理员审核 → 结果记录" 工单模式 |
| **日志统一化** | 所有用户和管理员的操作统一记录在 OperationLog 表，不再分表记录 |
| **封禁独立化** | 封禁状态通过 Users.is_banned / Shops.is_banned 独立字段表达，不再与软删除 is_active 混用 |

### 1.2 分层职责

```
Router → Service → DAO → Model (数据模型层)
```

数据模型层（`models/`）只负责：
- 定义表结构、字段、类型、约束
- 定义字段关系（ForeignKey / ReverseRelation）
- 定义索引
- 不包含任何业务逻辑

### 1.3 通用字段

所有继承 `BaseModel` 的表都自动拥有以下字段：

| 字段名 | 类型 | 说明 |
|:---|:---|:---|
| `id` | 各表自定 | 主键，自增 |
| `created_at` | Datetime | 创建时间，`auto_now_add`，不可手动修改 |
| `updated_at` | Datetime | 最后更新时间，`auto_now` |
| `is_active` | Boolean (default=True) | 软删除标记。查询时默认只查 `is_active=True` |

---

## 2. 文件组织

```
models/
  __init__.py       统一导出，按依赖顺序导入
  base.py           基类（BaseModel）
  dict.py           字典体系（DictTypes / DictData / ShopDictRel）
  users.py          用户模块（Users / Activities / Favorites / Messages）
  shops.py          店铺模块（Shops / Menu / Ratings）
  images.py         图片模块（Images）
  interaction.py    互动模块（ShopComments / CommentReplies / ShopQuestions / QuestionAnswers / ContentLikes）
  governance.py     治理模块（Complaints / ShopEditRequests）
  logs.py           日志模块（OperationLog）
```

### 2.1 文件划分逻辑

| 功能区 | 对应文件 | 包含模型 |
|:---|:---|:---|
| 基础 | `base.py` | BaseModel（所有模型的基类） |
| 标签管理 | `dict.py` | 字典类型 + 字典数据 + 多对多关联 |
| 身份与空间 | `users.py` | 用户、动态、收藏、消息 |
| 资产底座 | `shops.py` | 店铺、菜单、评分 |
| 资源文件 | `images.py` | 图片（多态关联） |
| 用户互动 | `interaction.py` | 评论、回复、提问、回答 |
| 治理审核 | `governance.py` | 举报、勘误反馈 |
| 审计追踪 | `logs.py` | 统一操作日志 |

### 2.2 删除/合并的历史文件

| 旧文件 | 去向 |
|:---|:---|
| `bans.py` | 已删除。Bans表取消，`is_banned` 字段移至 Users/Shops，封禁历史由 OperationLog 记录 |
| `complaints.py` | 已删除。内容移入 `governance.py`，ComplaintHandlers 表合并入 Complaints |
| `reviews.py` | 已删除。ShopEditRequests 移入 `governance.py` |
| `admin_logs.py` | 已删除。合并入统一 OperationLog |

---

## 3. 模型全景关系图

```
Users ──┬── Activities      (user行为时间线)
         ├── Favorites       (user ↔ shop，多对多)
         ├── Messages        (recipient/sender)
         ├── ShopComments    (一级评论作者)
         ├── CommentReplies  (二级回复作者)
         ├── ShopQuestions   (一级问题作者)
         ├── QuestionAnswers (二级回答作者)
         ├── Complaints      (举报发起者 / 处理者 admin)
         └── ShopEditRequests(勘误提交者 / 审核者 admin)

Shops ──┬── ShopDictRel → DictData → DictTypes   (标签体系，多对多)
         ├── Menu           (菜单项)
         ├── Ratings        (评分，user+shop唯一约束)
         ├── Favorites      (被收藏)
         ├── ShopComments   (一级评论归属)
         ├── CommentReplies (经评论归属店铺)
         ├── ShopQuestions  (一级问题归属)
         ├── QuestionAnswers(经问题归属店铺)
         ├── Activities     (动态关联店铺，前端跳转用)
         ├── Complaints     (被举报实体，多态)
         ├── ShopEditRequests(待修改店铺)
         └── Shops.merged_into (自引用，店铺合并)
```

---

## 4. 字典体系

### 4.1 设计理念

"一切可枚举的标签属性通过字典管理"。

店铺的**品类**、**区域**、**就餐方式**等所有可穷举打标签的属性，均通过 DictTypes + DictData + ShopDictRel 三表实现。当需要新增标签类型时，只需在 DictData 中添加数据行，无需修改表结构。

### 4.2 DictTypes — 字典类型表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| code | VARCHAR(50) UNIQUE | 类型编码，如 `category`、`location_type`、`dining_method` |
| name | VARCHAR(50) UNIQUE | 类型名称，如"品类"、"区域"、"就餐方式" |
| target_table | VARCHAR(50) | 目标业务表名。合法值见 `constants.DICT_TARGET_TABLES`，当前为 `shops`、`complaints`、`users`、`menu_items` |
| description | VARCHAR(255) | 可选的类型描述 |
| sort_order | INT | 类型间的排序顺序 |

**预设的字典类型：**

| code | name | target_table |
|:---|:---|:---|
| `category` | 品类 | shops |
| `location_type` | 区域 | shops |
| `dining_method` | 就餐方式 | shops |

### 4.3 DictData — 字典数据表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| dict_type | FK → DictTypes | 所属字典类型 |
| code | VARCHAR(50) | 数据编码，同一类型内唯一。如 `hotpot`、`snacks` |
| name | VARCHAR(50) | 显示名称，如"火锅"、"小吃快餐" |
| value | VARCHAR(255) | 额外值（保留，可不使用） |
| sort_order | INT | 同一类型内的排序 |
| is_default | BOOLEAN | 是否为默认选中值 |
| extra | JSON | 扩展字段（图标、颜色等） |

**唯一约束：** `(dict_type_id, code)` — 同一类型下不允许重复编码。

### 4.4 ShopDictRel — 店铺字典关联表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| shop | FK → Shops | 店铺 |
| dict_data | FK → DictData | 字典数据项 |

**唯一约束：** `(shop_id, dict_data_id)` — 一个店铺不会两次关联同一个字典项。

**典型查询模式：**
```python
# 获取店铺的所有标签（品类 + 区域 + 就餐方式）
relations = await ShopDictRel.filter(shop_id=shop_id).prefetch_related("dict_data", "dict_data__dict_type")
```

---

## 5. 用户模块

### 5.1 Users — 用户表

| 字段 | 类型 | 约束 | 说明 |
|:---|:---|:---:|:---|
| id | INT PK | | 自增主键 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 登录用户名，同时作为平台显示名 |
| password | VARCHAR(255) | NOT NULL | bcrypt 加密后的密码 |
| phone | VARCHAR(20) | UNIQUE, NOT NULL | 手机号 |
| email | VARCHAR(100) | UNIQUE, NOT NULL | 邮箱 |
| avatar | VARCHAR(255) | NULL | 头像URL |
| bio | TEXT | NULL | 个人简介 |
| gender | VARCHAR(10) | NULL | `male` / `female` / `other` |
| role | INT | default=0 | `0`=普通用户，`1`=管理员 |
| is_banned | BOOLEAN | default=False | 是否被封禁。`True`=封禁中，登录和写操作全部冻结 |

**设计说明：**

- **`username` 即显示名**。原设计有独立的 `nickname` 字段，已删除。用户在注册和登录时看到的都是同一个 username，避免混淆。
- **`is_banned` 独立于 `is_active`**。`is_active=False` 表示用户主动注销（软删除），`is_banned=True` 表示管理员封禁。前者用户不可恢复，后者管理员可随时解封。

### 5.2 Activities — 动态表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| user | FK → Users | 产生动态的用户 |
| type | VARCHAR(50) | 动态类型：`comment` / `rating` / `favorite` / `add_shop` / `reply` / `question` |
| target_id | INT | 关联目标ID（评论ID / 店铺ID等） |
| target_type | VARCHAR(50) | 目标实体类型，辅助前端判断跳转路径 |
| content | VARCHAR(255) | 预格式化的展示文本，如"评论了店铺" |
| shop | FK → Shops (NULL) | **关联店铺ID**，用于前端生成跳转链接。这是动态表的核心跳转字段 |

**设计说明：**

- 这是**用户主页时间线**的专用表。所有用户在平台上的公开行为聚合展示在此。
- `shop` 字段是跳转关键——前端拿到 `shop_id` 即可生成 `/shops/{id}` 链接，无需额外查询。
- 当前动态记录由各 Service 手动创建（待改进）。**后续应改为 Tortoise ORM 的 post_save 信号机制自动生成**，详见 `services/activity_signals.py` 占位文件。

### 5.3 Favorites — 收藏表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| user | FK → Users | 收藏用户 |
| shop | FK → Shops | 被收藏店铺 |
| sort_order | INT (default=0) | 排序序号，数值越小越靠前（预留，当前未启用） |

**索引：** `(user_id, created_at)` — 按收藏时间倒序查询。

**设计说明：**

- 收藏切换（toggle）通过 `is_active` 实现：收藏时创建新记录（`is_active=True`），取消收藏时软删除（`is_active=False`）。不删除物理记录以保留操作历史。
- 无 `(user_id, shop_id)` 唯一约束，允许同一用户对同一店铺多次收藏/取消的操作历史。

### 5.4 Messages — 消息表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| recipient | FK → Users | 接收用户 |
| sender | FK → Users (NULL) | 发送用户（系统消息时为 NULL） |
| type | VARCHAR(50) | 消息类型：`announcement` / `reply_comment` / `comment_like` / `complaint_result` 等 |
| title | VARCHAR(100) | 消息标题 |
| content | TEXT | 消息内容 |
| related_entity_type | VARCHAR(50) | 关联实体类型（供前端跳转） |
| related_entity_id | INT | 关联实体ID（供前端跳转） |
| is_read | BOOLEAN (default=False) | 是否已读 |

**索引：** `(recipient_id, created_at)` — 按用户+时间查询消息列表。

---

## 6. 店铺模块

### 6.1 Shops — 店铺表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| name | VARCHAR(100) | 店铺名称 |
| view_count | INT (default=0) | 浏览量（冗余字段） |
| favorite_count | INT (default=0) | 收藏数（冗余字段） |
| comment_count | INT (default=0) | 评论数（冗余字段） |
| average_rating | FLOAT (default=0.0) | 平均评分（冗余字段） |
| aliases | JSON | 别名列表，如 `["老店名", "曾用名"]` |
| merged_into | FK → Shops (NULL, 自引用) | 合并后目标店铺ID |
| is_banned | BOOLEAN (default=False) | 是否被封禁 |

**设计说明：**

店铺表只保留**核心客观字段**。已删除的字段及原因：

| 已删除字段 | 原因 |
|:---|:---|
| description（描述） | 主观填写的描述易误导他人 |
| price_range（价格段） | 主观且易过时 |
| business_hours（营业时间） | 易变且不准确 |
| dining_methods（就餐方式） | 通过 DictData 字典管理 |
| address_detail（详细地址） | 用户可能没去过，填不准；找店靠名字搜索而非地址 |
| tags（标签） | 通过 DictData + ShopDictRel 字典体系管理 |

`average_rating` 使用 `FloatField` 而非 `DecimalField`，因为 Decimal 在 JSON 序列化时会变成字符串（如 `"4.5"`），前端需要额外转换。

### 6.2 Menu — 菜单项表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| shop | FK → Shops | 所属店铺 |
| name | VARCHAR(100) | 菜品名称 |
| price | FLOAT | 价格（元） |
| description | TEXT | 菜品描述 |

**设计说明：**

- 菜品图片统一通过 `Images` 表管理（`entity_type='menu_item'`），不再存储在 `extra` JSON 字段中。
- 菜单项按 `id` 升序排列，不支持用户自定义排序。
- `price` 原为 Decimal 类型（JSON 序列化为字符串），现改为 Float。

### 6.3 Ratings — 评分表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| user | FK → Users | 评分用户 |
| shop | FK → Shops | 被评店铺 |
| score | INT | 评分值（1-5） |

**唯一约束：** `(user_id, shop_id)` — 每个用户对每个店铺只能评分一次（可修改，不可重复创建）。

---

## 7. 资源模块

### 7.1 Images — 图片表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 自增主键（预留大量余量） |
| url | VARCHAR(255) | 图片访问路径 |
| entity_type | VARCHAR(32) | 关联实体类型：`shop` / `menu_item` / `shop_comment` / `comment_reply` |
| entity_id | BIGINT | 关联实体的主键ID |
| file_size | INT (NULL) | 文件大小（字节） |
| width | INT (NULL) | 图片宽度（像素） |
| height | INT (NULL) | 图片高度（像素） |
| mime_type | VARCHAR(50) (NULL) | MIME 类型，如 `image/jpeg` |
| extra | JSON (NULL) | 扩展字段，用于存储 alt 文本等业务自定义信息 |

**索引：** `(entity_type, entity_id)` — 按实体查询其全部图片。

### 7.2 设计说明

**多态关联方案：**

`entity_type + entity_id` 是行业通用的多态关联方案（Django 的 GenericForeignKey、Laravel 的 morphs 均采用此模式）。此处**主动选择不使用数据库外键约束**，原因如下：

| 方案 | 优点 | 缺点 |
|:---|:---|:---|
| 多态关联（当前） | 一张表即可，新实体类型无需加列 | 无 FK 级联，需在 DAO 层手动处理 |
| 多 FK 列 | 有 FK 约束和 ON DELETE CASCADE | 每新增一种实体就加一列，大部分行为 NULL，浪费空间 |

**级联删除策略：**

在 DAO 层统一处理。凡软删除一个实体时，同步软删除其关联图片：

```python
# 示例：删除评论时同步删除图片
comment.is_active = False
await comment.save()
await Images.filter(entity_type='shop_comment', entity_id=comment.id).update(is_active=False)
```

---

## 8. 互动模块

### 8.1 设计说明

互动模块将评论区和问答区完全分离，各自独立两张表（一级内容 + 二级回复），不再像旧设计那样用 `type` 字段混用在一张 Comments 表里。

**二级回复的扁平设计：**

```
ShopComments(id=1) "这家店不错"
  ├─ CommentReplies(id=10, reply_to_user=NULL)       "同意！你吃了啥？"  →  @无前缀
  └─ CommentReplies(id=11, reply_to_user=user_10)    "吃了番茄牛腩"     →  @username前缀
```

- 所有二级回复通过 `comment_id` 外键直接关联到所属的一级评论
- `reply_to_user` 记录被回复人，**仅用于前端在内容前加 `@username` 前缀**
- 无 `parent_id` 自引用，意味着回复之间没有嵌套层级，全部平铺
- 查询时：`CommentReplies.filter(comment_id=X).order_by('created_at')`，一次性取出所有回复

### 8.2 ShopComments — 一级评论表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 自增主键 |
| shop | FK → Shops | 关联店铺 |
| user | FK → Users | 评论作者 |
| content | TEXT | 评论内容 |
| like_count | INT (default=0) | 点赞数（冗余字段） |
| reply_count | INT (default=0) | 二级回复数（冗余字段） |

**索引：** `(shop_id, created_at)` — 按店铺查看评论列表。

### 8.3 CommentReplies — 二级回复表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 自增主键 |
| comment | FK → ShopComments | 所属一级评论 |
| user | FK → Users | 回复作者 |
| content | TEXT | 回复内容 |
| reply_to_user | FK → Users (NULL) | 被回复用户（用于 @username 前缀） |
| like_count | INT (default=0) | 点赞数（冗余字段） |

**索引：** `(comment_id, created_at)` — 按一级评论加载所有回复。

### 8.4 ShopQuestions — 一级问题表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 自增主键 |
| shop | FK → Shops | 关联店铺 |
| user | FK → Users | 提问用户 |
| title | VARCHAR(100) | 问题概括（短，必填） |
| content | TEXT (NULL) | 问题描述（长，可选） |
| like_count | INT (default=0) | 点赞数（冗余字段） |

**索引：** `(shop_id, created_at)` — 按店铺查看问题列表。

### 8.5 QuestionAnswers — 二级回答表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 自增主键 |
| question | FK → ShopQuestions | 所属一级问题 |
| user | FK → Users | 回答用户 |
| content | TEXT | 回答内容 |
| reply_to_user | FK → Users (NULL) | 被回复用户（用于 @username 前缀） |
| like_count | INT (default=0) | 点赞数（冗余字段） |

**索引：** `(question_id, created_at)` — 按问题加载所有回答。

### 8.6 ContentLikes — 内容点赞表（多态）

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 自增主键 |
| user | FK → Users | 点赞用户 |
| entity_type | VARCHAR(32) | 被点赞内容类型：`shop_comment` / `comment_reply` / `shop_question` / `question_answer` |
| entity_id | BIGINT | 被点赞内容ID |

**索引：**
- `(entity_type, entity_id)` — 查某条内容的所有点赞
- `(user_id, entity_type, entity_id, created_at)` — 查某用户是否已点赞

**设计说明：**

- 采用多态关联（`entity_type` + `entity_id`），一张表覆盖四种互动内容的点赞，无需为每种内容建独立的点赞表。
- 不设立唯一约束，点赞切换通过继承自 BaseModel 的 `is_active` 软删除实现：
  - 首次点赞 → insert（`is_active=True`）
  - 取消点赞 → `is_active=False`
  - 再次点赞 → `is_active=True`（复用记录，保留操作历史）
- 各内容的 `like_count` 字段为冗余计数，在 DAO 层同步更新。

---

## 9. 治理模块

### 9.1 设计说明

治理模块采用统一的 **"工单"模式**：用户提交 → 管理员审核 → 结果通知。

与 ShopEditRequests 保持一致的设计规范：

| 状态 | 含义 |
|:---|:---|
| `pending` | 待处理 |
| `approved` | 已通过（触发相应业务操作） |
| `rejected` | 已驳回（附驳回理由） |

### 9.2 Complaints — 举报表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| user | FK → Users | 举报发起用户 |
| complainant_type | VARCHAR(32) | 被举报内容类型：`comment` / `shop` / `image` |
| complainant_id | INT | 被举报内容ID |
| reason_code | VARCHAR(50) | 举报原因编码，来自 DictData 字典 |
| description | TEXT (NULL) | 补充说明 |
| status | VARCHAR(20) | `pending` / `approved` / `rejected` |
| admin | FK → Users (NULL) | 处理管理员 |
| action | VARCHAR(50) (NULL) | 处理动作：`delete_comment` / `ban_shop` / `remove_image` / `dismiss` |
| result_description | TEXT (NULL) | 处理结果描述/备注 |

**索引：** `(complainant_type, complainant_id)` — 查询某个实体的所有举报记录。

**设计说明：**

- `complainant_type + complainant_id` 采用多态关联（同 Images 模式），无 FK 约束，级联删除在 DAO 层处理。
- `action` 由管理员选择，决定了 Service 层实际执行的操作（删除评论 / 封禁店铺 / 移除图片）。
- 原来的 ComplaintHandlers 表已合并至此表。本课程设计场景中，一个举报只需要一次处理，不需要多条处理历史。

### 9.3 ShopEditRequests — 店铺勘误/重复反馈表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| shop | FK → Shops | 待修改的店铺 |
| user | FK → Users | 提交用户 |
| proposed_data | JSON | 提议修改的内容（格式见下方） |
| status | VARCHAR(20) | `pending` / `approved` / `rejected` |
| admin | FK → Users (NULL) | 审核管理员 |

**索引：** `(status, created_at)` — 管理员查询待处理列表。

**`proposed_data` JSON 格式：**

**勘误类型（type=correction）：**
```json
{
  "type": "correction",
  "changes": {
    "name": "新店铺名",
    "area": {"dict_data_id": 10},
    "category": {"dict_data_id": 3}
  },
  "reason": "这家店改名了"
}
```

**重复类型（type=merge）：**
```json
{
  "type": "merge",
  "candidate_shop_ids": [1, 3, 5],
  "reason": "这三家其实是同一家店的不同分店"
}
```

**设计说明：**

`proposed_data` 使用 JSON 字段而非固定列，因为勘误和重复两种场景需要提交的数据结构完全不同。JSON 格式在 Service 层进行业务规则校验。

---

## 10. 日志模块

### 10.1 OperationLog — 统一操作日志

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 自增主键 |
| operator | FK → Users (NULL) | 操作用户（未登录或系统操作时为 NULL） |
| operator_name | VARCHAR(50) (NULL) | 操作时的用户名（冗余，用户删除后保留追溯能力） |
| action | VARCHAR(50) | 操作动作。如 `view_shop` / `comment` / `ban_user` / `approve_edit` |
| target_type | VARCHAR(50) | 操作对象类型。如 `shop` / `user` / `comment` / `complaint` |
| target_id | INT (NULL) | 操作对象ID |
| detail | JSON (NULL) | 操作详情，可包含 before/after 快照、封禁原因等上下文 |
| ip_address | VARCHAR(45) (NULL) | 客户端IP |
| user_agent | TEXT (NULL) | 客户端设备信息 |
| session_id | VARCHAR(64) (NULL) | 会话ID（未登录用户追踪用） |
| is_active | BOOLEAN (default=True) | 日志软删除标记。API 不提供任何删除接口，仅用于系统内部维护 |

**索引：** `(operator_id, created_at)` / `(action, created_at)` / `(target_type, target_id)`

### 10.2 设计说明

**合并来源：**

OperationLog 替代了原来的两张日志表：

| 原表 | 记录内容 | 去向 |
|:---|:---|:---|
| UserBehaviorLogs | 用户浏览、收藏等行为 | ✅ 合并入 OperationLog |
| AdminOperationLog | 管理员封禁、审核等操作 | ✅ 合并入 OperationLog |

**使用场景：**

| 场景 | 查询条件 |
|:---|:---|
| 用户操作历史 | `operator_id=X, action NOT IN ('view_shop')` |
| 管理员审计 | `action LIKE 'ban_%' OR action LIKE 'approve_%'` |
| 对象变更历史 | `target_type='shop', target_id=42` |

---

## 11. 基类

### 11.1 BaseModel

```python
class BaseModel(TimestampMixin, SoftDeleteMixin, Model):
    class Meta:
        abstract = True
```

所有数据模型（除 OperationLog 外）均继承 BaseModel。它由两个 Mixin 组合：

**TimestampMixin：**
- `created_at` — 创建时间，`auto_now_add=True`，不可手动修改
- `updated_at` — 最后更新时间，`auto_now=True`

**SoftDeleteMixin：**
- `is_active` — 布尔值，default=True。`False` 表示逻辑删除

**请注意：**

`is_active` 在 Users 和 Shops 上**不代表封禁状态**。封禁由独立的 `is_banned` 字段表达。`is_active` 仅用于：

| 场景 | `is_active` | `is_banned` |
|:---|:---:|:---:|
| 正常状态 | True | False |
| 被封禁 | True | True |
| 用户注销/店铺合并删除 | False | False |

---

## 12. 附录

### 12.1 迁移状态

已通过 `aerich init-db` 在 `foodiehub_db` 数据库重建全部表结构。
迁移文件：`backend/migrations/models/0_20260528162829_init.py`

| 表名 | 迁移中 | 模型中 | 备注 |
|:---|:---:|:---:|:---|
| dict_types | ✅ | ✅ | |
| dict_data | ✅ | ✅ | |
| shop_dict_rel | ✅ | ✅ | |
| shops | ✅ | ✅ | 已精简字段 |
| menu_items | ✅ | ✅ | `price` 改为 FLOAT，`extra` 已删除 |
| ratings | ✅ | ✅ | |
| users | ✅ | ✅ | 已删除 nickname，增加 is_banned |
| activities | ✅ | ✅ | 新增 shop_id 字段 |
| favorites | ✅ | ✅ | |
| messages | ✅ | ✅ | |
| images | ✅ | ✅ | 新增 file_size/width/height/mime_type |
| complaints | ✅ | ✅ | 新增 admin/action/result_description |
| shop_edit_requests | ✅ | ✅ | |
| content_likes | ✅ | ✅ | 新增，多态点赞表 |
| operation_logs | ✅ | ✅ | 新增，统一日志表 |
| shop_comments | ✅ | ✅ | 新增，一级评论 |
| comment_replies | ✅ | ✅ | 新增，二级回复 |
| shop_questions | ✅ | ✅ | 新增，一级问题 |
| question_answers | ✅ | ✅ | 新增，二级回答 |
| ~~comments~~ | ❌已删 | ❌已删 | 已拆分为 shop_comments + comment_replies |
| ~~comments_likes~~ | ❌已删 | ❌已删 | 替换为 content_likes |
| ~~user_behavior_logs~~ | ❌已删 | ❌已删 | 替换为 operation_logs |
| ~~complaint_handlers~~ | ❌已删 | ❌已删 | 合并入 complaints |
| ~~bans~~ | ❌已删 | ❌已删 | 替换为 users/shops.is_banned |
| ~~admin_operation_logs~~ | ❌已删 | ❌已删 | 替换为 operation_logs |

### 12.2 TODO — 待实现事项

| 事项 | 优先级 | 说明 |
|:---|:---:|:---|
| Activity 自动生成信号 | 高 | 见 `services/activity_signals.py` 占位文件 |
| DAO 层图片级联删除 | 高 | 软删除实体时同步软删除关联的 Images 记录 |
| DictTypes.target_table 校验 | 低 | Service 层校验，确保值在 `constants.DICT_TARGET_TABLES` 中 |

### 12.3 常量文件

`backend/constants.py` 存放全局纯常量，与 `config.py`（读取 .env 的运行时配置）分离：

```python
# 图片上传限制
ALLOWED_IMAGE_TYPES       # 允许的图片 MIME 类型
MAX_IMAGE_SIZE            # 最大图片大小（2MB）

# 分页
PAGE_SIZE_DEFAULT         # 默认每页 20 条
PAGE_SIZE_MAX             # 最大每页 100 条

# 用户角色
ROLE_USER                 # 普通用户（0）
ROLE_ADMIN                # 管理员（1）

# 字典目标表枚举
DICT_TARGET_TABLES        # 合法的 target_table 值列表

# 审核状态
STATUS_PENDING            # pending
STATUS_APPROVED           # approved
STATUS_REJECTED           # rejected
```
