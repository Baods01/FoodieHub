# user_dao.py — 用户数据访问层

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/user_dao.py`
> 对应模型：`models/users.py` → `Users`

---

## 概述
UserDAO 负责用户表（Users）的全部数据访问操作。该 DAO 处理用户注册、登录、查询、信息更新和软删除。其他关联数据（评论、收藏、问答、统计）已从本 DAO 移出，由对应的专门 DAO 处理。登录方法考虑了封禁用户的安全处理：被封禁用户在普通登录查询中返回 None，以避免向未登录者暴露封禁状态。

---

## 数据模型预览
### Users — 用户表
| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | IntField (pk) | 用户唯一标识 |
| username | CharField(50, unique) | 登录用户名（同时作为显示名） |
| password | CharField(255) | 加密后的密码（bcrypt） |
| phone | CharField(20, unique) | 手机号 |
| email | CharField(100, unique) | 电子邮箱，用于通知 |
| avatar | CharField(255, nullable) | 头像图片 URL |
| bio | TextField (nullable) | 个人简介 |
| gender | CharField(10, nullable) | 性别：male/female/other |
| role | IntField | 角色：0=普通用户，1=管理员 |
| is_banned | BooleanField | 是否被封禁：True=封禁中，False=正常 |
| is_active | BooleanField | 软删除标记（继承自 BaseModel），默认 True |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

---

## 方法概览
### 单条查询
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id` | user_id: int | `Optional[Users]` | 根据 ID 获取用户 |
| `get_by_username` | username: str | `Optional[Users]` | 根据用户名获取用户 |
| `get_by_phone` | phone: str | `Optional[Users]` | 根据手机号获取用户 |
| `get_by_email` | email: str | `Optional[Users]` | 根据邮箱获取用户 |
| `get_by_account` | account: str | `Optional[Users]` | 登录用：按用户名/手机号/邮箱匹配（仅正常用户） |
| `get_by_account_include_banned` | account: str | `Optional[Users]` | 登录用（含封禁用户）：区分"账号不存在"和"被封禁" |

### 列表
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `list` | is_active, is_banned, keyword, page, page_size | `dict` | 管理员后台：用户列表，分页+筛选+搜索 |

### 写操作
| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `exists` | **kwargs | `bool` | 检查用户是否存在 |
| `check_duplicate` | username, phone, email | `Optional[str]` | 注册查重：返回已存在字段名 |
| `create` | username, password, phone, email, **kwargs | `Users` | 创建新用户 |
| `update` | user_id: int, **kwargs | `Optional[Users]` | 更新用户信息（含头像） |
| `delete` | user_id: int | `bool` | 软删除用户（注销账号） |

---

## 方法详述

### get_by_id — 根据ID获取用户

**描述：** 根据用户 ID 获取用户记录，仅返回未被软删除的用户。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | — | 用户 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Optional[Users]` | 用户模型实例，不存在或已软删除则返回 None |

**使用示例：**
```python
user = await UserDAO.get_by_id(user_id=1)
if user:
    print(f"用户名: {user.username}, 角色: {user.role}")
```

**业务场景：**
- 获取当前登录用户信息
- 业务逻辑中需要引用用户信息时

**实现逻辑（概述）：**
调用 `Users.get_or_none(id=user_id, is_active=True)` 查询。

---

### get_by_username — 根据用户名获取用户

**描述：** 根据用户名精确查找用户记录。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| username | str | 是 | — | 用户名 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Optional[Users]` | 用户模型实例，不存在或已软删除则返回 None |

**使用示例：**
```python
user = await UserDAO.get_by_username(username="zhangsan")
```

**业务场景：**
- 检查用户名是否被占用（结合 check_duplicate 使用）
- 个人主页通过用户名加载用户信息

**实现逻辑（概述）：**
调用 `Users.get_or_none(username=username, is_active=True)` 查询。

---

### get_by_phone — 根据手机号获取用户

**描述：** 根据手机号精确查找用户记录。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| phone | str | 是 | — | 手机号 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Optional[Users]` | 用户模型实例，不存在或已软删除则返回 None |

**使用示例：**
```python
user = await UserDAO.get_by_phone(phone="13800138000")
```

**业务场景：**
- 检查手机号是否被占用
- 通过手机号查找用户（用于分享等功能）

**实现逻辑（概述）：**
调用 `Users.get_or_none(phone=phone, is_active=True)` 查询。

---

### get_by_email — 根据邮箱获取用户

**描述：** 根据邮箱精确查找用户记录。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| email | str | 是 | — | 电子邮箱 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Optional[Users]` | 用户模型实例，不存在或已软删除则返回 None |

**使用示例：**
```python
user = await UserDAO.get_by_email(email="user@example.com")
```

**业务场景：**
- 检查邮箱是否被占用
- 通过邮箱查找用户

**实现逻辑（概述）：**
调用 `Users.get_or_none(email=email, is_active=True)` 查询。

---

### get_by_account — 登录用账户查询

**描述：** 按用户名/手机号/邮箱匹配查找用户，**仅返回正常用户（is_active=True）**。这是普通登录接口使用的查询方法，被封禁用户返回 None，登录提示"账号或密码错误"（不暴露封禁信息给未登录者）。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| account | str | 是 | — | 登录账号（用户名、手机号或邮箱） |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Optional[Users]` | 用户模型实例（正常用户），账号不存在或已封禁则返回 None |

**使用示例：**
```python
user = await UserDAO.get_by_account(account="13800138000")
if user and verify_password(password, user.password):
    # 登录成功
    pass
```

**业务场景：**
- 用户登录时，根据输入账号（可能是用户名、手机号或邮箱）查询用户
- 与密码验证结合完成登录流程

**实现逻辑（概述）：**
使用 `Q(username=account) | Q(phone=account) | Q(email=account)` 组合查询条件，同时过滤 `is_active=True`，返回第一个匹配结果或 None。

---

### get_by_account_include_banned — 登录用账户查询（含封禁用户）

**描述：** 按用户名/手机号/邮箱匹配查找用户，**包含所有状态的用户（包括被封禁者）**。用于区分"账号不存在"和"账号被封禁"两种情况，让 Service 层可以给出不同的错误提示。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| account | str | 是 | — | 登录账号（用户名、手机号或邮箱） |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Optional[Users]` | 用户模型实例（任意状态），账号不存在则返回 None |

**使用示例：**
```python
user = await UserDAO.get_by_account_include_banned(account="13800138000")
if user is None:
    return {"error": "账号不存在"}
elif user.is_banned:
    return {"error": "账号已被封禁，请联系管理员"}
else:
    # 进行密码验证...
    pass
```

**业务场景：**
- 登录接口需要区分不同错误信息时（先查此方法，再查普通方法）
- 帮助页面展示封禁提示（不暴露给未登录者）

**实现逻辑（概述）：**
使用 `Q(username=account) | Q(phone=account) | Q(email=account)` 组合查询条件，不过滤 is_active，取第一条记录。

---

### list — 用户列表（管理员后台）

**描述：** 管理员后台用分页查询，支持按状态筛选和关键词搜索。关键词同时匹配用户名、手机号和邮箱。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| is_active | Optional[bool] | 否 | None | 按软删除状态筛选（None 表示不筛选） |
| is_banned | Optional[bool] | 否 | None | 按封禁状态筛选（None 表示不筛选） |
| keyword | Optional[str] | 否 | None | 关键词搜索（匹配用户名/手机号/邮箱） |
| page | int | 否 | 1 | 页码，从 1 开始 |
| page_size | int | 否 | 20 | 每页条数 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `dict` | 包含 items（用户列表）、total、page、page_size 的字典 |

**使用示例：**
```python
# 查询所有未封禁的正常用户
result = await UserDAO.list(is_active=True, is_banned=False, page=1, page_size=20)
print(f"共 {result['total']} 位用户")
for u in result["items"]:
    print(f"- {u.username} ({u.email})")

# 关键词搜索
result = await UserDAO.list(keyword="138", page=1, page_size=10)
```

**业务场景：**
- 管理员后台用户管理页面
- 后台用户筛选（正常/封禁/已注销）
- 后台用户搜索功能

**实现逻辑（概述）：**
构建查询链：先应用 is_active 过滤（若非 None），再应用 is_banned 过滤（若非 None），最后应用 keyword 模糊匹配。先查总数，再分页查询。

---

### exists — 检查用户是否存在

**描述：** 通过任意字段组合检查用户是否存在，支持任意过滤条件。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| **kwargs | dict | 是 | — | 任意字段名和值的组合，如 `username="test"` |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `bool` | 存在返回 True，否则返回 False |

**使用示例：**
```python
if await UserDAO.exists(username="test"):
    print("用户名已存在")

if await UserDAO.exists(phone="13800138000", is_active=True):
    print("该手机号已被使用且账号正常")
```

**业务场景：**
- 注册前快速检查字段是否被占用
- 业务逻辑中判断某条件的用户是否存在

**实现逻辑（概述）：**
调用 `Users.filter(**kwargs).exists()` 执行存在性检查。

---

### check_duplicate — 注册查重

**描述：** 在用户注册时检查用户名、手机号、邮箱是否已被占用。返回第一个已存在的字段名，若都不存在返回 None。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| username | str | 是 | — | 用户名 |
| phone | str | 是 | — | 手机号 |
| email | str | 是 | — | 电子邮箱 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Optional[str]` | 已存在字段名（"username"/"phone"/"email"），都不存在返回 None |

**使用示例：**
```python
duplicate_field = await UserDAO.check_duplicate(
    username="zhangsan",
    phone="13800138000",
    email="zhangsan@example.com",
)
if duplicate_field:
    return {"error": f"{duplicate_field}已被注册"}
# 继续注册流程...
```

**业务场景：**
- 用户注册时检查唯一字段是否重复
- Service 层判断注册请求是否可以继续

**实现逻辑（概述）：**
按顺序检查三个字段：先查用户名是否存在，再查手机号，最后查邮箱。发现第一个存在即返回该字段名，三个都不存在返回 None。注意：仅检查 `is_active=True` 的用户。

---

### create — 创建用户

**描述：** 创建新用户记录，插入数据库。密码应由调用方预先加密（bcrypt），此处仅存储。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| username | str | 是 | — | 用户名 |
| password | str | 是 | — | 加密后的密码（bcrypt 加密后的字符串） |
| phone | str | 是 | — | 手机号 |
| email | str | 是 | — | 电子邮箱 |
| **kwargs | dict | 否 | {} | 可选字段，如 avatar、bio、gender 等 |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Users` | 创建的用户模型实例 |

**使用示例：**
```python
user = await UserDAO.create(
    username="zhangsan",
    password=bcrypt_hash, # 预加密的密码
    phone="13800138000",
    email="zhangsan@example.com",
    avatar="/static/avatars/default.png",
)
```

**业务场景：**
- 用户注册新账号
- 管理员后台手动创建用户

**实现逻辑（概述）：**
调用 `Users.create(...)` 插入数据库，返回创建的模型实例。

---

### update — 更新用户信息

**描述：** 更新指定用户的信息，支持部分字段更新（仅更新传入的非 None 参数）。可用于更新头像、简介、性别等。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | — | 用户 ID |
| **kwargs | dict | 是 | — | 要更新的字段名和值的组合，如 `avatar="/new/avatar.png"` |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `Optional[Users]` | 更新后的用户模型实例，用户不存在或已软删除则返回 None |

**使用示例：**
```python
user = await UserDAO.update(
    user_id=1,
    avatar="/static/avatars/new_avatar.png",
    bio="这是我的个人简介",
    gender="male",
)
```

**业务场景：**
- 用户修改个人资料（头像、简介、性别等）
- 管理员修改用户信息

**实现逻辑（概述）：**
通过 `get_or_none` 获取用户实例，使用 `setattr` 逐个赋值更新的字段，最后调用 `.save()` 保存。

---

### delete — 软删除用户（注销账号）

**描述：** 软删除指定用户，将 `is_active` 设为 False。该操作不会真正从数据库删除用户记录。用户注销后，其发布的店铺、评论、问答等数据是否保留由业务规则决定（通常保留但标记用户信息为"已注销"）。

**参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| user_id | int | 是 | — | 用户 ID |

**返回：**
| 类型 | 说明 |
|:---|:---|
| `bool` | 是否成功删除（用户存在且未被软删除返回 True，否则 False） |

**使用示例：**
```python
success = await UserDAO.delete(user_id=1)
if success:
    print("用户账号已注销")
```

**业务场景：**
- 用户主动注销账号
- 管理员删除用户账号

**实现逻辑（概述）：**
通过 `get_or_none` 获取用户，设置 `is_active=False` 后保存。注意：调用方需在 Service 层自行处理关联数据的清理（如收藏、问答等），本方法仅处理 Users 表本身。

---

## 附：已移出的方法说明

以下方法已从 UserDAO 移出，请使用对应的专门 DAO：

| 方法 | 目标 DAO 文件 |
|:---|:---|
| `get_user_comments()` | `comment_dao.py` |
| `get_user_favorites()` | `favorite_dao.py` |
| `get_user_questions_count()` | `question_dao.py`（通过 `list_by_user` 实现） |
| `get_user_stats()`（跨表聚合统计） | `analytics_dao.py` |
| `create_user_behavior_log()` | 改用 `LogDAO.log()` |
| `get_user_behavior_logs()` | 改用 `LogDAO.list(operator_id=...)` |