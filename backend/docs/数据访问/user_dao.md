# user_dao.py — 用户数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/user_dao.py`

---

## 概述

user_dao 仅处理 Users 表。用户的评论/收藏/问答等关联数据分别由各自的 DAO 文件提供（详见文件尾 TODO 列表）。

---

## 方法列表

### 单条查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(user_id)` | id | `Optional[Users]` | 按 ID 查 |
| `get_by_username(username)` | 用户名 | `Optional[Users]` | 精确查 |
| `get_by_phone(phone)` | 手机号 | `Optional[Users]` | |
| `get_by_email(email)` | 邮箱 | `Optional[Users]` | |
| `get_by_account(account)` | 用户名/手机/邮箱 | `Optional[Users]` | ⭐ 登录用，仅查正常用户（is_active=True） |
| `get_by_account_include_banned(account)` | 同上 | `Optional[Users]` | ⭐ 含封禁用户，用于区分"账号不存在"和"账号被封禁" |

### 列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `list(is_active, is_banned, keyword, page, page_size)` | 全部可选 | `dict` | ⭐ 管理员后台用户列表，支持筛选+搜索+分页 |

### 写操作

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `exists(**kwargs)` | 任意字段 | `bool` | 检查用户是否存在 |
| `check_duplicate(username, phone, email)` | 三个字段 | `Optional[str]` | ⭐ 注册查重，返回已存在的字段名或 None |
| `create(username, password, phone, email, **kwargs)` | 四必填 | `Users` | ⭐ 注册 |
| `update(user_id, **kwargs)` | id + 字段 | `Optional[Users]` | 更新信息（含头像） |
| `delete(user_id)` | id | `bool` | 软删除（注销） |

---

## 典型用法

```python
from dao import UserDAO

# 注册
if await UserDAO.check_duplicate("new_user", "138xxxx", "a@b.com"):
    return "已存在"
user = await UserDAO.create(
    username="new_user", password="hashed_pw",
    phone="138xxxx", email="a@b.com",
)

# 登录
user = await UserDAO.get_by_account_include_banned("new_user")
if not user:
    return "账号不存在"
if not user.is_active:
    return f"账号已被封禁"
if not verify_password(password, user.password):
    return "密码错误"

# 管理员查询用户列表
result = await UserDAO.list(is_banned=True, page=1, page_size=20)
```

---

## 注意事项

1. **`get_by_account` 自动过滤 `is_active=False`**，封禁用户不会被查到（返回 None，提示"账号或密码错误"）。如需区分"不存在"和"被封禁"，请用 `get_by_account_include_banned`。
2. **被移出的方法（请到对应文件实现）：**
   - 用户评论列表 → `comment_dao.py`
   - 用户收藏列表 → `favorite_dao.py`
   - 用户问答统计 → `question_dao.py`
   - 跨表统计 → `analytics_dao.py`
   - 操作日志 → `log_dao.py`
