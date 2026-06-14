# 文档更新日志
此文档更新日志章节记录每次操作所解决的问题，只追加不修改。

## 更新日期：2026-06-05
### 更新摘要
根据后端 models/ 目录的实际模型代码，同步更新 README.md 文档，使各章节与实际表结构一致。

### 更新详情
- **文件组织**：`governance.py` 描述由旧 `Complaints / ShopEditRequests` 更新为 `Feedback`；新增 `history.py`（ViewHistory）条目至目录树和职能划分表；历史删除文件表补充 `shop_edit_requests.py`
- **全景关系图**：`Complaints`→`Feedback`、`ShopEditRequests`→移除、`ShopDictRel`→`DictRel`；新增 `ViewHistory` 关系线（用户侧+店铺侧）
- **新增 Section 7.2 ViewHistory**：完整描述 `ViewHistory` 表的字段、唯一约束、继承 BaseModel 及设计说明
- **治理模块重写**（Section 9）：由旧 `Complaints` 表 + `ShopEditRequests` 表的两节内容，替换为统一的 `Feedback` 单表模型（8字段 + 2索引 + 5条设计说明）
- **迁移状态表**：`feedbacks` 加入活跃行；`complaints`/`shop_edit_requests` 移入已删除区；新增 `view_history` 行
- **字段修正**：OperationLog.target_type 示例值 `complaint`→`feedback`；Shops.comment_count 描述 `评论数`→`讨论数`


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
  dict.py           字典体系（DictTypes / DictData / DictRel）
  users.py          用户模块（Users / Activities / Favorites / Messages）
  shops.py          店铺模块（Shops / Menu / Ratings）
  images.py         图片模块（Images）
  interaction.py    互动模块（ShopComments / CommentReplies / ShopQuestions / QuestionAnswers / ContentLikes）
  interaction.py    互动模块（ShopComments / CommentReplies / ShopQuestions / QuestionAnswers / ContentLikes）
  history.py        浏览历史（ViewHistory）
  governance.py     治理模块（Feedback）
  logs.py           日志模块（OperationLog）
```

### 2.1 文件划分逻辑

| 功能区 | 对应文件 | 包含模型 |
|:---|:---|:---|
| 基础 | `base.py` | BaseModel（所有模型的基类） |
| 标签管理 | `dict.py` | 字典类型 + 字典数据 + 多态关联 |
| 身份与空间 | `users.py` | 用户、动态、收藏、消息 |
| 资产底座 | `shops.py` | 店铺、菜单、评分 |
| 资源文件 | `images.py` | 图片（多态关联） |
| 用户互动 | `interaction.py` | 评论、回复、提问、回答 |
| 浏览历史 | `history.py` | 浏览记录（独立表） |
| 治理审核 | `governance.py` | 统一反馈工单 |
| 审计追踪 | `logs.py` | 统一操作日志 |

### 2.2 删除/合并的历史文件

| 旧文件 | 去向 |
|:---|:---|
| `bans.py` | 已删除。Bans表取消，`is_banned` 字段移至 Users/Shops，封禁历史由 OperationLog 记录 |
| `complaints.py` | 已删除。内容合并入 `governance.py` 的统一 Feedback 表 |
| `reviews.py` | 已删除。内容合并入 `governance.py` 的统一 Feedback 表 |
| `shop_edit_requests.py` | 已删除。内容合并入 `governance.py` 的统一 Feedback 表 |
| `admin_logs.py` | 已删除。合并入统一 OperationLog |

---

## 3. 模型全景关系图

```
Users ──┬── Activities      (user行为时间线)
         ├── Favorites       (user ↔ shop，多对多)
         ├── Messages        (recipient/sender)
         ├── ViewHistory     (user浏览记录)
         ├── ShopComments    (一级评论作者)
         ├── CommentReplies  (二级回复作者)
         ├── ShopQuestions   (一级问题作者)
         ├── QuestionAnswers (二级回答作者)
         └── Feedback        (反馈工单提交者)

Shops ──┬── DictRel → DictData → DictTypes   (标签体系，多对多)
         ├── Menu           (菜单项)
         ├── Ratings        (评分，user+shop唯一约束)
         ├── Favorites      (被收藏)
         ├── ViewHistory    (浏览记录)
         ├── ShopComments   (一级评论归属)
         ├── CommentReplies (经评论归属店铺)
         ├── ShopQuestions  (一级问题归属)
         ├── QuestionAnswers(经问题归属店铺)
         ├── Activities     (动态关联店铺，前端跳转用)
         ├── Feedback       (被反馈实体，多态)
         └── Shops.merged_into (自引用，店铺合并)
```

---

## 4. 字典体系

### 4.1 设计理念

"一切可枚举的标签属性通过字典管理"。

店铺的**品类**、**区域**、**就餐方式**等所有可穷举打标签的属性，均通过 DictTypes + DictData + DictRel 三表实现。当需要新增标签类型时，只需在 DictData 中添加数据行，无需修改表结构。

### 4.2 DictTypes — 字典类型表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| name | VARCHAR(50) UNIQUE | 类型名称（业务唯一标识），如"品类""区域""就餐方式" |
| target_table | VARCHAR(50) | 所属业务表名。标记这个字典类型属于哪张表，供前端/开发者筛选。合法值见 `constants.DICT_TARGET_TABLES` |
| description | VARCHAR(255) | 可选的类型描述 |
| sort_order | INT | 类型间的排序顺序 |

**预设的字典类型：**

| name | target_table | 用途 |
|:---|:---|:---|
| 品类 | shops | 店铺的菜品类别（火锅、烧烤等） |
| 区域 | shops | 店铺的地理区域（华农西门、泰山区等） |
| 就餐方式 | shops | 堂食、自取、外卖 |

### 4.3 DictData — 字典数据表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| dict_type | FK → DictTypes | 所属字典类型 |
| name | VARCHAR(50) | 标签名称，如"火锅""华农西门"。同一类型下唯一 |
| sort_order | INT | 同一类型内的排序 |
| is_default | BOOLEAN | 是否为默认选中值 |
| extra | JSON | 扩展字段（图标、颜色等） |

**删除的字段：** `code`（用 name 替代）、`value`（从未使用）

**唯一约束：** `(dict_type_id, name)` — 同一类型下名称唯一。

### 4.4 DictRel — 字典数据关联表（多态）

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| entity_type | VARCHAR(32) | 关联实体类型，如 `shop` / `complaint` / `user` 等 |
| entity_id | BIGINT | 关联实体主键 ID |
| dict_data | FK → DictData | 字典数据ID |

**唯一约束：** `(entity_type, entity_id, dict_data_id)` — 防止重复关联。
**索引：** `(entity_type, entity_id)` — 快速查某个实体的全部标签。

**设计说明：** 采用多态关联，取代原有的 `ShopDictRel`。任何实体（店铺、举报、用户等）需要标签属性，直接复用 DictRel，无需新建关联表。与 Images、ContentLikes 保持统一的多态设计风格。

**典型查询模式：**
```python
# 获取店铺的所有标签
rels = await DictRel.filter(entity_type='shop', entity_id=shop_id).prefetch_related('dict_data', 'dict_data__dict_type')
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
| comment_count | INT (default=0) | 讨论数（冗余字段） |
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
| tags（标签） | 通过 DictData + DictRel 字典体系管理 |

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
| uploader_id | INT (NULL) | 上传者用户ID |

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

### 7.2 ViewHistory — 浏览历史表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| user | FK → Users | 浏览用户 |
| shop | FK → Shops | 被浏览店铺 |
| viewed_at | Datetime (auto_now) | 最近浏览时间 |

**唯一约束：** `(user_id, shop_id)` — 每个用户-店铺对只有一条记录，重复访问时 `viewed_at` 自动更新。
**索引：** 通过唯一约束覆盖。

**设计说明：**

- 独立于 `OperationLog`（审计日志），专用于前端"我的浏览记录"功能。
- 继承 BaseModel，拥有 `id`、`created_at`、`updated_at`、`is_active` 字段。`(user_id, shop_id)` 的 `unique_together` 约束保证每个用户-店铺对只有一条记录，重复访问仅更新 `viewed_at`，不产生新行。
- `viewed_at` 使用 `auto_now=True`，每次访问自动刷新。
- 软删除（`is_active=False`）表示用户主动清除浏览记录。

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

治理模块将旧 `Complaints`（举报）与 `ShopEditRequests`（勘误）合并为一张统一的 **Feedback** 表，通过 `type` 字段区分业务类型。

统一的 **"工单"模式**：用户提交 → 管理员审核 → 结果通知。

| 状态 | 含义 |
|:---|:---|
| `pending` | 待处理 |
| `approved` | 已通过（触发相应业务操作） |
| `rejected` | 已驳回（附驳回理由） |

### 9.2 Feedback — 统一反馈工单表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| user | FK → Users | 提交用户（反馈发起者） |
| type | VARCHAR(20) | 反馈类型：`complaint`（举报） / `edit_request`（勘误） |
| target_type | VARCHAR(20) | 反馈对象类型：`shop` / `comment` / `image` |
| target_id | INT | 被反馈对象ID |
| reason | FK → DictData | 反馈原因（字典数据，前端可选值由 `/dict/data?type_name=反馈原因` 提供） |
| description | TEXT (NULL) | 用户填写的补充描述 |
| status | VARCHAR(20) default=`pending` | 审核状态：`pending` / `approved` / `rejected` |
| admin | FK → Users (NULL) | 处理管理员 |

**索引：**
- `(status, created_at)` — 管理员按状态筛选待处理工单
- `(target_type, target_id)` — 查询某个实体的全部反馈记录

**设计说明：**

- **单表统一**：`type` 字段区分举报和勘误，不再需要两张独立的表和完全不同的字段结构。
- **原因字典化**：`reason` 通过 FK 引用 DictData，举报原因/勘误原因均可通过 DictTypes 管理，前端无需硬编码。
- **描述文本**：原 Complaints 的 `description` 字段保留（补充说明），原 ShopEditRequests 的 `proposed_data` JSON 不再使用——改为纯文本描述 + 原因字典的组合。
- **处理动作**：原 Complaints 的 `action` 字段已移除。审核通过（`approved`）后由 Service 层根据 `type` + `target_type` 自动判断执行（如 `complaint` + `comment` → 删除评论）。
- **合并历史**：原 ComplaintHandlers 表（旧多步骤处理记录）已废弃，合并前的数据并入当前 Feedbacks 表。

---

## 10. 日志模块

### 10.1 OperationLog — 统一操作日志

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 自增主键 |
| operator | FK → Users (NULL) | 操作用户（未登录或系统操作时为 NULL） |
| operator_name | VARCHAR(50) (NULL) | 操作时的用户名（冗余，用户删除后保留追溯能力） |
| action | VARCHAR(50) | 操作动作。如 `view_shop` / `comment` / `ban_user` / `approve_edit` |
| target_type | VARCHAR(50) | 操作对象类型。如 `shop` / `user` / `comment` / `feedback` |
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
迁移文件：
- `0_20260528172517_init.py` — 完整建表（含 DictRel 多态、精简后无 code/value 的字典）

| 表名 | 迁移中 | 模型中 | 备注 |
|:---|:---:|:---:|:---|
| dict_types | ✅ | ✅ | |
| dict_data | ✅ | ✅ | |
| dict_rels | ✅ | ✅ | 多态关联，替代原 shop_dict_rel |
| shops | ✅ | ✅ | 已精简字段 |
| menu_items | ✅ | ✅ | `price` 改为 FLOAT，`extra` 已删除 |
| ratings | ✅ | ✅ | |
| users | ✅ | ✅ | 已删除 nickname，增加 is_banned |
| activities | ✅ | ✅ | 新增 shop_id 字段 |
| favorites | ✅ | ✅ | |
| messages | ✅ | ✅ | |
| images | ✅ | ✅ | 新增 file_size/width/height/mime_type/uploader_id |
| feedbacks | ✅ | ✅ | 统一反馈工单，type 区分 complaint / edit_request |
| content_likes | ✅ | ✅ | 新增，多态点赞表 |
| operation_logs | ✅ | ✅ | 新增，统一日志表 |
| shop_comments | ✅ | ✅ | 新增，一级评论 |
| comment_replies | ✅ | ✅ | 新增，二级回复 |
| shop_questions | ✅ | ✅ | 新增，一级问题 |
| question_answers | ✅ | ✅ | 新增，二级回答 |
| ~~comments~~ | ❌已删 | ❌已删 | 已拆分为 shop_comments + comment_replies |
| ~~comments_likes~~ | ❌已删 | ❌已删 | 替换为 content_likes |
| ~~user_behavior_logs~~ | ❌已删 | ❌已删 | 替换为 operation_logs |
| ~~complaint_handlers~~ | ❌已删 | ❌已删 | 合并入 feedbacks |
| view_history | ✅ | ✅ | 新增，浏览历史独立表 |
| ~~complaints~~ | ❌已删 | ❌已删 | 替换为 feedbacks（type='complaint'） |
| ~~shop_edit_requests~~ | ❌已删 | ❌已删 | 替换为 feedbacks（type='edit_request'） |
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

---
